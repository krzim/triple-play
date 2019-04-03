from uuid import UUID

from flask import current_app, request
from flask_jwt_extended import jwt_required

from api_gateway.extensions import db
from api_gateway.scheduler import InvalidTriggerArgs
from api_gateway.security import permissions_accepted_for_resources, ResourcePermissions
from api_gateway.server.decorators import with_resource_factory
from api_gateway.server.problem import Problem
from http import HTTPStatus
from api_gateway.serverdb.scheduledtasks import ScheduledTask

with_task = with_resource_factory('Scheduled task', lambda task_id: ScheduledTask.query.filter_by(id=task_id).first())


def validate_uuids(uuids):
    invalid_uuids = []
    for uuid in uuids:
        try:
            UUID(uuid)
        except ValueError:
            invalid_uuids.append(uuid)
    return invalid_uuids


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['read']))
def get_scheduler_status():
    return {"status": current_app.running_context.scheduler.scheduler.state}, HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['update', 'execute']))
def update_scheduler_status():
    status = request.get_json()['status']
    updated_status = current_app.running_context.scheduler.scheduler.state
    if status == "start":
        updated_status = current_app.running_context.scheduler.start()
        current_app.logger.info('Scheduler started. Status {0}'.format(updated_status))
    elif status == "stop":
        updated_status = current_app.running_context.scheduler.stop()
        current_app.logger.info('Scheduler stopped. Status {0}'.format(updated_status))
    elif status == "pause":
        updated_status = current_app.running_context.scheduler.pause()
        current_app.logger.info('Scheduler paused. Status {0}'.format(updated_status))
    elif status == "resume":
        updated_status = current_app.running_context.scheduler.resume()
        current_app.logger.info('Scheduler resumed. Status {0}'.format(updated_status))
    return {"status": updated_status}, HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['read']))
def read_all_scheduled_tasks():
    page = request.args.get('page', 1, type=int)
    return [task.as_json() for task in
            ScheduledTask.query.paginate(page, current_app.config['ITEMS_PER_PAGE'], False).items], HTTPStatus.OK


def invalid_uuid_problem(invalid_uuids):
    return Problem(
        HTTPStatus.BAD_REQUEST,
        'Invalid scheduled task.',
        'Specified UUIDs {} are not valid.'.format(invalid_uuids))


def scheduled_task_name_already_exists_problem(name, operation):
    return Problem.from_crud_resource(
        HTTPStatus.BAD_REQUEST,
        'scheduled task',
        operation,
        'Could not {} scheduled task. Scheduled task with name {} already exists.'.format(operation, name))


invalid_scheduler_args_problem = Problem(HTTPStatus.BAD_REQUEST, 'Invalid scheduled task.',
                                         'Invalid scheduler arguments.')


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['create', 'execute']))
def create_scheduled_task():
    data = request.get_json()
    invalid_uuids = validate_uuids(data['workflows'])
    if invalid_uuids:
        return invalid_uuid_problem(invalid_uuids)
    task = ScheduledTask.query.filter_by(name=data['name']).first()
    if task is None:
        try:
            task = ScheduledTask(**data)
        except InvalidTriggerArgs:
            return invalid_scheduler_args_problem
        else:
            db.session.add(task)
            db.session.commit()
            return task.as_json(), HTTPStatus.CREATED
    else:
        return scheduled_task_name_already_exists_problem(data['name'], 'create')


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['read']))
@with_task('read', 'scheduled_task_id')
def read_scheduled_task(scheduled_task_id):
    return scheduled_task_id.as_json(), HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['update', 'execute']))
@with_task('update', 'scheduled_task_id')
def update_scheduled_task(scheduled_task_id):
    data = request.get_json()
    invalid_uuids = validate_uuids(data.get('workflows', []))
    if invalid_uuids:
        return invalid_uuid_problem(invalid_uuids)
    if 'name' in data:
        same_name = ScheduledTask.query.filter_by(name=data['name']).first()
        if same_name is not None and same_name.id != data['id']:
            return scheduled_task_name_already_exists_problem(same_name, 'update')
    try:
        scheduled_task_id.update(data)
    except InvalidTriggerArgs:
        return invalid_scheduler_args_problem
    else:
        db.session.commit()
        return scheduled_task_id.as_json(), HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['delete']))
@with_task('delete', 'scheduled_task_id')
def delete_scheduled_task(scheduled_task_id):
        db.session.delete(scheduled_task_id)
        db.session.commit()
        return None, HTTPStatus.NO_CONTENT


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('scheduler', ['execute']))
@with_task('control', 'scheduled_task_id')
def control_scheduled_task(scheduled_task_id):
        action = request.get_json()['action']
        if action == 'start':
            scheduled_task_id.start()
        elif action == 'stop':
            scheduled_task_id.stop()
        db.session.commit()
        return {}, HTTPStatus.OK
