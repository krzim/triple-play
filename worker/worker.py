from collections import deque
import asyncio
import logging
import sys
from typing import Union

import aiohttp
import aioredis

from common.message_types import message_dumps, message_loads, NodeStatusMessage, WorkflowStatusMessage, StatusEnum, \
    JSONPatch, JSONPatchOps
from common.config import config
from common.helpers import connect_to_redis_pool
from common.workflow_types import Node, Action, Condition, Transform, Trigger, ParameterVariant, Workflow, \
    workflow_dumps, workflow_loads, ConditionException

logging.basicConfig(level=logging.INFO, format="{asctime} - {name} - {levelname}:{message}", style='{')
logger = logging.getLogger("WORKER")


class Worker:
    def __init__(self, workflow: Workflow = None, start_action: str = None, redis: aioredis.Redis = None,
                 session: aiohttp.ClientSession = None):
        self.workflow = workflow
        self.start_action = start_action if start_action is not None else self.workflow.start
        self.accumulator = {}
        self.in_process = {}
        self.redis = redis
        self.session = session
        self.token = None

    @staticmethod
    async def get_workflow(redis: aioredis.Redis):
        """
            Continuously monitors the workflow queue for new work
        """
        while True:
            logger.info("Waiting for workflows...")
            workflow = await redis.brpoplpush(sourcekey=config.REDIS_WORKFLOW_QUEUE,
                                              destkey=config.REDIS_WORKFLOWS_IN_PROCESS,
                                              timeout=config.get_int("WORKER_TIMEOUT", 30))

            if workflow is None:  # We've timed out with no work. Guess we'll die now...
                sys.exit(1)

            yield workflow_loads(workflow)

    @staticmethod
    async def run():
        async with connect_to_redis_pool(config.REDIS_URI) as redis,\
                aiohttp.ClientSession(json_serialize=message_dumps) as session:
            async for workflow in Worker.get_workflow(redis):
                # Setup worker launch the event loop
                worker = Worker(workflow, redis=redis, session=session)
                logger.info(f"Starting execution of workflow: {workflow.name}")

                message = WorkflowStatusMessage.execution_started(worker.workflow.execution_id,
                                                                                  worker.workflow.id_,
                                                                                  worker.workflow.name)
                await worker.send_message(message)

                try:
                    await worker.execute_workflow()
                except Exception:
                    logger.exception(f"Failed execution of workflow: {workflow.name}")
                else:
                    logger.info(f"Completed execution of workflow: {workflow.name}")
                finally:
                    await worker.send_message(WorkflowStatusMessage.execution_completed(worker.workflow.execution_id,
                                                                                        worker.workflow.id_,
                                                                                        worker.workflow.name))

                # Clean up workflow in process queue
                await redis.lrem(config.REDIS_WORKFLOWS_IN_PROCESS, 0, workflow_dumps(workflow))
        await Worker.shutdown()

    @staticmethod
    async def shutdown():
        # Clean up any unfinished tasks (shouldn't really be any though)
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]

        logger.info('Canceling outstanding tasks')
        await asyncio.gather(*tasks, return_exceptions=True)

    async def cancel_subgraph(self, node):
        """
            Cancels the task related to the current node as well as the tasks related to every child of that node.
            Also removes them from the worker's internal in_process queue.
        """
        dependents = self.workflow.get_dependents(node)
        cancelled_tasks = set()

        for task in asyncio.all_tasks():
            for _, arg in task._coro.cr_frame.f_locals.items():  # Where the args of a coro are stored...trust me
                if isinstance(arg, Node):
                    if arg in dependents:
                        self.in_process.pop(arg.id_)
                        task.cancel()
                        cancelled_tasks.add(task)

        await asyncio.gather(*cancelled_tasks, return_exceptions=True)

    async def execute_workflow(self):
        """
            Do a simple BFS to visit and schedule each node in the workflow. We assume every node will run and thus
            preemptively schedule them all. We will clean up any nodes that will not run due to conditions or triggers
        """
        visited = {self.start_action}
        queue = deque([self.start_action])
        tasks = set()

        while queue:
            node = queue.pop()
            parents = {n.id_: n for n in self.workflow.predecessors(node)} if node is not self.start_action else {}
            children = {n.id_: n for n in self.workflow.successors(node)}
            self.in_process[node.id_] = node

            if isinstance(node, Action):
                node.execution_id = self.workflow.execution_id  # the app needs this as a key for the redis queue

            elif isinstance(node, Trigger):
                raise NotImplementedError

            tasks.add(asyncio.create_task(self.schedule_node(node, parents, children)))

            for child in sorted(children.values(), reverse=True):
                if child not in visited:
                    queue.appendleft(child)
                    visited.add(child)

        # TODO: Figure out a clean way of handling the exceptions here. Cancelling subgraphs throws CancelledErrors.
        # Launch the results accumulation task and wait for all the results to come in
        results_task = asyncio.create_task(self.get_action_results())
        exceptions = await asyncio.gather(*tasks, results_task, return_exceptions=True)
        for e in exceptions:
            if isinstance(e, Exception) and not isinstance(e, asyncio.CancelledError):
                try:
                    raise e
                except:
                    logger.exception(f"Exception while executing Workflow:{self.workflow}")

    async def evaluate_condition(self, condition, parents, children):
        """
            TODO: This will change when we implement a better UI element for it. For now, if an action is given a user
            defined name like "Hello World", it would be referenced by the variable name "Hello_World" in the
            conditional script. All whitespace in the action name is replaced by '_'. This is clearly problematic
            if a user has an action named "Hello World" as well as "Hello_World". In this case, we cannot be sure
            which is being referenced in the conditional and must raise an exception.
        """
        logger.debug(f"Attempting evaluation of: {condition.label}-{self.workflow.execution_id}")
        try:
            child_id = condition(parents, children, self.accumulator)
            selected_node = children.pop(child_id)
            await self.send_message(NodeStatusMessage.success_from_node(condition, self.workflow.execution_id, selected_node))
            logger.info(f"Condition selected node: {selected_node.label}-{self.workflow.execution_id}")

            # We preemptively schedule all branches of execution so we must cancel all "false" branches here
            [await self.cancel_subgraph(child) for child in children.values()]

            self.in_process.pop(condition.id_)
            self.accumulator[condition.id_] = selected_node

        except ConditionException as e:
            logger.exception(f"Worker received error for {condition.name}-{self.workflow.execution_id}")
            await self.send_message(NodeStatusMessage.failure_from_node(condition, self.workflow.execution_id, error=repr(e)))

        except Exception:
            logger.exception("Something happened in Condition evaluation")

    async def execute_transform(self, transform, parent):
        """ Execute an transform and ship its result """
        logger.debug(f"Attempting evaluation of: {transform.label}-{self.workflow.execution_id}")
        try:
            result = transform(self.accumulator[parent.id_])  # run transform on parent's result
            await self.send_message(NodeStatusMessage.success_from_node(transform, self.workflow.execution_id, result))
            logger.info(f"Transform {transform.label}-succeeded with result: {result}")

            self.accumulator[transform.id_] = result
            self.in_process.pop(transform.id_)

        # TODO: figure out exactly what can be raised by the possible transforms
        except Exception as e:
            logger.exception(f"Worker received error for {transform.name}-{self.workflow.execution_id}")
            await self.send_message(NodeStatusMessage.failure_from_node(transform, self.workflow.execution_id, error=repr(e)))

    async def get_globals(self):
        url = config.API_GATEWAY_URI.rstrip('/') + '/api'

        # TODO: make this secure
        if self.token is None:
            async with self.session.post(url + "/auth", json={"username": config.WALKOFF_USERNAME,
                                                              "password": config.WALKOFF_PASSWORD}, timeout=5) as resp:
                resp_json = await resp.json()
                self.token = resp_json["refresh_token"]
                logger.debug("Successfully logged into WALKOFF")

        headers = {"Authorization": f"Bearer {self.token}"}
        async with self.session.post(url + "/auth/refresh", headers=headers, timeout=5) as resp:
            resp_json = await resp.json()
            access_token = resp_json["access_token"]
            logger.debug("Successfully refreshed WALKOFF JWT")

        headers = {"Authorization": f"Bearer {access_token}"}
        async with self.session.get(url + "/globals", headers=headers, timeout=5) as resp:
            globals_ = await resp.json(loads=workflow_loads)
            logger.debug(f"Got globals: {globals_}")
            return globals_

    async def dereference_params(self, action: Action):
        #TODO: update this to pull from the database
        global_vars = await self.get_globals()
        for param in action.parameters:
            if param.variant == ParameterVariant.STATIC_VALUE:
                continue

            elif param.variant == ParameterVariant.ACTION_RESULT:
                if param.reference in self.accumulator:
                    param.value = self.accumulator[param.reference]

            elif param.variant == ParameterVariant.WORKFLOW_VARIABLE:
                if param.reference in self.workflow.workflow_variables:
                    param.value = self.workflow.workflow_variables[param.reference]

            elif param.variant == ParameterVariant.GLOBAL:
                if param.reference in global_vars:
                    param.value = self.accumulator[param.reference]

            else:
                logger.error(f"Unable to defeference parameter:{param} for action:{action}")
                break

            param.reference = None
            param.variant = ParameterVariant.STATIC_VALUE

    async def schedule_node(self, node, parents, children):
        """ Waits until all dependencies of an action are met and then schedules the action """
        while not all(parent.id_ in self.accumulator for parent in parents.values()):
            await asyncio.sleep(0)

        if isinstance(node, Action):
            await self.dereference_params(node)
            await self.send_message(NodeStatusMessage.executing_from_node(node, self.workflow.execution_id))
            await self.redis.lpush(f"{node.app_name}:{node.priority}", workflow_dumps(node))

        elif isinstance(node, Condition):
            await self.send_message(NodeStatusMessage.executing_from_node(node, self.workflow.execution_id))
            await self.evaluate_condition(node, parents, children)

        elif isinstance(node, Transform):
            if len(parents) > 1:
                logger.error(f"Error scheduling {node.name}: Transforms cannot have more than 1 incoming connection.")
            await self.send_message(NodeStatusMessage.executing_from_node(node, self.workflow.execution_id))
            await self.execute_transform(node, parents.popitem()[1])

        elif isinstance(node, Trigger):
            raise NotImplementedError

        # TODO: decide if we want pending action messages and uncomment this line
        # await self.send_message(NodeStatus.pending_from_node(node, workflow.execution_id))
        logger.info(f"Scheduled {node}")

    async def get_action_results(self):
        """ Continuously monitors the results queue until all scheduled actions have been completed """
        read_messages_queue = f"{self.workflow.execution_id}::read"
        while len(self.in_process) > 0:
            msg = await self.redis.brpoplpush(self.workflow.execution_id, read_messages_queue, timeout=5)

            if msg is None:
                continue

            msg: NodeStatusMessage = message_loads(msg)
            # Ensure that the received NodeStatusMessage is for an action we launched
            if msg.execution_id == self.workflow.execution_id and msg.node_id in self.in_process:
                if msg.status == StatusEnum.EXECUTING:
                    logger.info(f"App started execution of: {msg.label}-{msg.execution_id}")
                    continue  # We know another message is coming and have nothing else to do

                elif msg.status == StatusEnum.SUCCESS:
                    self.accumulator[msg.node_id] = msg.result
                    logger.info(f"Worker received result for: {msg.label}-{msg.execution_id}")

                elif msg.status == StatusEnum.FAILURE:
                    self.accumulator[msg.node_id] = msg.result
                    await self.cancel_subgraph(self.workflow.nodes[msg.node_id])  # kill the children!
                    logger.info(f"Worker recieved error \"{msg.result}\" for: {msg.label}-{msg.execution_id}")

                else:
                    logger.error(f"Unknown message status received: {msg}")
                    msg = None

                await self.send_message(msg)

            else:
                logger.error(f"Message received for unknown execution: {msg}")

            # Keep our redis queues clean
            await self.redis.lrem(read_messages_queue, 0, message_dumps(msg))
            node = self.in_process.pop(msg.node_id, None)
            await self.redis.lrem(config.REDIS_ACTIONS_IN_PROCESS, 0, workflow_dumps(node))


        # Clean up our redis mess
        await self.redis.delete(read_messages_queue)

    def make_patch(self, message, root, op, value_only=False, white_list=None, black_list=None):
        if white_list is None and black_list is None:
            raise ValueError("Either white_list or black_list must be provided")

        if white_list is not None and black_list is not None:
            raise ValueError("Either white_list or black_list must be provided, not both")

        # convert blacklist to whitelist and grab those attrs from the message
        white_list = set(message.__slots__).difference(black_list) if black_list is not None else white_list

        if value_only and len(white_list) != 1:
            raise ValueError("value_only can only be set if a single key is in white_list")

        if value_only:
            (key,) = white_list
            values = getattr(message, key)
        else:
            values = {k: getattr(message, k) for k in message.__slots__ if k in white_list}

        return JSONPatch(op, path=root, value=values)

    def get_patches(self, message):
        patches = []
        if isinstance(message, NodeStatusMessage):
            root = f"/node_statuses/{message.node_id}"
            if message.status == StatusEnum.EXECUTING:
                patches.append(self.make_patch(message, root, JSONPatchOps.ADD, black_list={"result", "completed_at"}))

            elif message.status == StatusEnum.SUCCESS:
                patches.append(self.make_patch(message, root, JSONPatchOps.REPLACE, black_list={}))
                # patches.append(self.make_patch(message, root, JSONPatchOps.REPLACE, white_list={"status", "result", "completed_at"}))

            elif message.status == StatusEnum.FAILURE:
                patches.append(self.make_patch(message, root, JSONPatchOps.REPLACE, black_list={}))
                # patches.append(self.make_patch(message, root, JSONPatchOps.REPLACE, white_list={"status"}))
                # patches.append(self.make_patch(message, root, JSONPatchOps.ADD, white_list={"error", "completed_at"}))

        elif isinstance(message, WorkflowStatusMessage):
            if message.status == StatusEnum.EXECUTING:
                for key in [attr for attr in message.__slots__ if getattr(message, attr)]:
                    patches.append(self.make_patch(message, f"/{key}", JSONPatchOps.REPLACE, value_only=True,
                                                   white_list={f"{key}"}))

            elif message.status == StatusEnum.COMPLETED or message.status == StatusEnum.ABORTED:
                patches.append(self.make_patch(message, f"/status", JSONPatchOps.REPLACE, value_only=True,
                                               white_list={"status"}))
                patches.append(self.make_patch(message, f"/completed_at", JSONPatchOps.REPLACE, value_only=True,
                                               white_list={"completed_at"}))

        return patches

    async def send_message(self, message: Union[NodeStatusMessage, WorkflowStatusMessage, None]):
        """ Forms and sends a JSONPatch message to the api_gateway to update the status of an action or workflow """

        if message is None:
            return None

        patches = self.get_patches(message)

        if len(patches) < 1:
            raise ValueError(f"Attempting to send improper message type: {type(message)}")

        params = {"event": message.status.value}
        url = f"{config.API_GATEWAY_URI}/api/internal/workflowstatus/{self.workflow.execution_id}"
        try:
            async with self.session.patch(url, json=patches, params=params, timeout=5) as resp:
                results = await resp.json()
                logger.debug(f"API-Gateway status update response: {results}")
                return results
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Could not send status message to {url}: {e!r}")
        except aiohttp.ClientTimeout as e:
            logger.error(f"Timeout while sending message to {url}: {e!r}")
        except Exception as e:
            logger.error(f"Unknown error while sending message to {url}: {e!r}")


if __name__ == "__main__":
    # Launch the worker event loop
    asyncio.run(Worker.run())
