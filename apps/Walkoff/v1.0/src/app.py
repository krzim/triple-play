import socket
import asyncio
import aiohttp
import time
import logging
import requests

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Unauthorized(Exception):
    pass


class UnknownResponse(Exception):
    pass


class NotConnected(Exception):
    pass

DEFAULT_TIMEOUT = 2
WALKOFF_ADDRESS_DEFAULT = "http://localhost:5000"

class Walkoff(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
    
    async def connect(self, timeout, username, password):
        timeout=DEFAULT_TIMEOUT
        try:
            response = await self._request('post', '/api/auth', timeout,
                                     data=dict(username=username, password=password))
        except:
            return False, 'TimedOut'

        status_code = response.status
        if status_code == 404:
            return False, 'WalkoffNotFound'
        elif status_code == 401:
            return False, 'AuthenticationError'
        elif status_code == 201:
            #returns access token and refresh token
            return response, 'Success'
        else:
            return 'Unknown response {}'.format(status_code), 'UnknownResponse'

    async def disconnect(self, timeout, refresh_token):
        timeout=DEFAULT_TIMEOUT
        new_refresh_token = self.refresh_token(DEFAULT_TIMEOUT, refresh_token)
        headers = self.retrieve_header(refresh_token)
        try:
            self._request('post', '/api/auth/logout', timeout, headers=headers, data=dict(refresh_token=new_refresh_token))
            return 'Success'
        except:
            return 'Connection timed out', 'TimedOut'

    # METRICS
    async def get_app_metrics(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return await self.standard_request('get', '/api/metrics/apps', timeout=DEFAULT_TIMEOUT, headers=headers)

    async def get_workflow_metrics(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return await self.standard_request('get', '/api/metrics/workflows', timeout=DEFAULT_TIMEOUT, headers=headers)

    # USERS
    async def get_all_users(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return await self.standard_request('get', '/api/users', timeout=DEFAULT_TIMEOUT, headers=headers)

    # WORKFLOWS
    async def get_all_workflows(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return await self.standard_request('get', '/api/playbooks', timeout=DEFAULT_TIMEOUT, headers=headers)

        # WORKFLOWS
    def all_workflows(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return self.standard_request('get', '/api/workflowqueue', timeout=DEFAULT_TIMEOUT, headers=headers)

    async def get_workflow_id(self, playbook_name, workflow_name, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        try:
            response = await self.request_with_refresh('get', '/api/playbooks', timeout=DEFAULT_TIMEOUT, headers=headers)
        # except Timeout:
        #     return 'Connection timed out', 'TimedOut'
        except Unauthorized:
            return 'Unauthorized credentials', 'Unauthorized'
        except NotConnected:
            return 'Not connected to Walkoff', 'NotConnected'
        except UnknownResponse:
            return 'Unknown error occurred', 'UnknownResponse'
        else:
            response = await response.json()
            playbook = next((playbook for playbook in response if playbook['name'] == playbook_name), None)
            if playbook is None:
                return 'Playbook not found', 'WorkflowNotFound'
            workflow = next((workflow for workflow in playbook['workflows'] if workflow['name'] == workflow_name), None)
            if workflow is None:
                return 'Workflow not found', 'WorkflowNotFound'
            else:
                return workflow['id'], 'Success'

    async def execute_workflow(self, workflow_id, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        data = {"workflow_id": workflow_id}
        r = await self.standard_request('post', '/api/workflowqueue', timeout, headers=headers, data=data)
        execution_id = r[0]['id']
        return execution_id, 'Success'

    def pause_workflow(self, execution_id, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        data = {"execution_id": execution_id, "status": "pause"}
        return self.standard_request('patch', '/api/workflowqueue', timeout, headers=headers, data=data)

    def resume_workflow(self, execution_id, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        data = {"execution_id": execution_id, "status": "resume"}
        return self.standard_request('patch', '/api/workflowqueue', timeout, headers=headers, data=data)

    def trigger(self, execution_ids, data, arguments, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        data = {"execution_ids": execution_ids, "data_in": data, "arguments": arguments}
        return self.standard_request('post', '/api/triggers/send_data', timeout, headers=headers, data=data)

    async def get_workflow_results(self, timeout, access_token):
        timeout=DEFAULT_TIMEOUT
        headers = self.retrieve_header(access_token)
        return await self.standard_request('get', '/api/workflowqueue', timeout, headers=headers)

    def wait_for_workflow_completion(self, execution_id, timeout, request_timeout,
                                     wait_between_requests, token):
        timeout=60*5
        wait_between_requests=0.1
        headers = self.retrieve_header(token)
        if timeout < request_timeout:
            return 'Function timeout must be greater than request timeout', 'InvalidInput'
        elif timeout < wait_between_requests:
            return 'Function timeout must be greater than wait between requests', 'InvalidInput'
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = self.request_with_refresh('get', '/api/workflowqueue/{}'.format(execution_id), timeout,
                                                     headers=headers)
                if response.status_code == 200:
                    response = response.json()
                    if response['status'] == 'completed':
                        return response
                time.sleep(wait_between_requests)
            # except Timeout:
            #     return 'Connection timed out', 'TimedOut'
            except Unauthorized:
                return 'Unauthorized credentials', 'Unauthorized'
            except NotConnected:
                return 'Not connected to Walkoff', 'NotConnected'
            except UnknownResponse:
                return 'Unknown error occurred', 'UnknownResponse'

    async def standard_request(self, method, address, timeout, headers=None, data=None, **kwargs):
        try:
            response = await self.request_with_refresh(method, address, timeout, headers=headers, data=data, **kwargs)
            if response.status == 400:
                return 'Bad Request', 'BadRequest'
            return await response.json(), 'Success'
        # except Timeout:
        #     return 'Connection timed out', 'TimedOut'
        except Unauthorized:
            return 'Unauthorized credentials', 'Unauthorized'
        except NotConnected:
            return 'Not connected to Walkoff', 'NotConnected'
        except UnknownResponse:
            return 'Unknown error occurred', 'UnknownResponse'

    # def _format_request_args(self, address, timeout, headers=None, data=None, **kwargs):
    #     address = '{0}{1}'.format(self.walkoff_address, address)
    #     args = kwargs
    #     args['timeout'] = timeout
    #     #old: if not (self.headers is None and headers is None):
    #     if not (headers is None):
    #         args['headers'] = headers # old: if headers is not None else self.headers
    #     if data is not None:
    #         args['json'] = data
    #     # if self.is_https:
    #     #     args['verify'] = walkoff.config.Config.CERTIFICATE_PATH
    #     return address, args
    async def fetch_http(self, method, url, **kwargs):
        session = aiohttp.ClientSession()
        async with session.get(url) as response:
            resp = await session.request(method = method, url = url, **kwargs) 
            json = await resp.json()
            status = resp.status
            return resp
            session.close()

    def _request(self, method, address, timeout=5, headers=None, data=None, **kwargs):
        address = '{0}{1}'.format(WALKOFF_ADDRESS_DEFAULT, address)
        args = kwargs
        args['timeout'] = timeout
        #old: if not (self.headers is None and headers is None):
        if not (headers is None):
            args['headers'] = headers # old: if headers is not None else self.headers
        if data is not None:
            args['json'] = data
        # if self.is_https:
        #     args['verify'] = walkoff.config.Config.CERTIFICATE_PATH
        if method == 'put':
            #return requests.put(address, **args)
            return self.fetch_http('PUT', address, **args)
        elif method == 'post':
            return self.fetch_http('POST', address, **args)
            #return requests.post(address, **args)
        elif method == 'get':
            return self.fetch_http('GET', address, **args)
            #requests.get(address, **args)
        elif method == 'delete':
            return self.fetch_http('DELETE', address, **args)
            #return requests.delete(address, **args)

    async def request_with_refresh(self, method, address, timeout, headers=None, data=None, **kwargs):
        response = await self._request(method, address, timeout, headers, data, **kwargs)
        if response.status != 401:
            return response
        else:
            response = await self._request(method, address, timeout, headers, data, **kwargs)
            if response.status == 401:
                raise Unauthorized
            else:
                return response

    async def refresh_token(self, timeout, token):
        headers = {'Authorization': 'Bearer {}'.format(token)}
        response = await self._request('post','/api/auth/refresh', timeout, headers=headers)
        if response.status == 401:
            raise Unauthorized
        elif response.status == 201:
            key = await response.json()
            # old return: self.reset_authorization(key['access_token'])
            # return refresh token instead
            return key['access_token']
        else:
            print(await response.json())
            raise UnknownResponse

    def reset_authorization(self, token):
        headers = {'Authorization': 'Bearer {}'.format(token)}
        return headers

    def retrieve_header(self, token):
        headers = {'Authorization': 'Bearer {}'.format(token)}
        return headers

    def shutdown(self, token):
        refresh_token = self.refresh_token(DEFAULT_TIMEOUT, token)
        headers = retrieve_header(refresh_token)
        try:
            self._request('post', '/api/auth/logout', DEFAULT_TIMEOUT, headers=headers,
                          data=dict(refresh_token=refresh_token))
        # except Timeout:
        #     logger.warning('Could not log out. Connection timed out')
        except:
            logger.warning('AHHHHHH')

if __name__ == "__main__":
    import argparse
    LOG_LEVELS = ("debug", "info", "error", "warn", "fatal", "DEBUG", "INFO", "ERROR", "WARN", "FATAL")
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", dest="log_level", choices=LOG_LEVELS, default="DEBUG")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format="{asctime} - {name} - {levelname}:{message}", style='{')
    logger = logging.getLogger("Walkoff")

    async def run():
        app = Walkoff(logger=logger)
        async with app.connect_to_redis_pool():
            await app.get_actions()

    asyncio.run(run())
