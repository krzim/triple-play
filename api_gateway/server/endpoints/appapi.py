from copy import deepcopy
import json
import yaml
from http import HTTPStatus

from flask_jwt_extended import jwt_required
from flask import jsonify, current_app, request

from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, StatementError

from api_gateway.config import Config
from api_gateway import helpers
# ToDo: investigate why these imports are needed (AppApi will not have valid reference to actions if this isn't here
from api_gateway.executiondb.action import ActionApi
from api_gateway.executiondb.appapi import AppApi, AppApiSchema
from api_gateway.security import permissions_accepted_for_resources, ResourcePermissions
from api_gateway.server.problem import Problem, unique_constraint_problem, improper_json_problem, invalid_input_problem
from api_gateway.server.decorators import with_resource_factory, is_valid_uid, paginate


def app_api_getter_name(app_api_name):
    return current_app.running_context.execution_db.session.query(AppApi).filter_by(name=app_api_name).first()


app_api_schema = AppApiSchema()
with_app_api_name = with_resource_factory('app_api', app_api_getter_name)


# ToDo: App APIs should be stored in some nosql db instead to avoid this
def add_locations(appapi):
    app_name = appapi['name']
    for action in appapi.get('actions', []):
        for param in action.get('parameters', []):
            param['location'] = f"{app_name}.{action['name']}:{param['name']}"
    return appapi


def remove_locations(appapi):
    for action in appapi.get('actions', []):
        for param in action.get('parameters', []):
            param.pop('location', None)
    return appapi


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('app_apis', ['read']))
def read_all_app_names():
    qr = current_app.running_context.execution_db.session.query(AppApi).order_by(AppApi.name).all()
    r = [result.name for result in qr]
    return r, HTTPStatus.OK


# ToDo: Delete this when testing is done, or it can be used by the umpire
# @jwt_required
# @permissions_accepted_for_resources(ResourcePermissions('app_apis', ['create']))
def create_app_api():
    data = request.data
    if request.files and 'file' in request.files:
        data = request.files['file'].read().decode('utf-8')

    data = json.loads(data)
    app_name = data['name']
    add_locations(data)
    try:
        # ToDo: make a proper common type for this when the other components need it
        app_api = app_api_schema.load(data)
        current_app.running_context.execution_db.session.add(app_api)
        current_app.running_context.execution_db.session.commit()
        current_app.logger.info(f"Created App API {app_api.name} ({app_api.id_})")
        return app_api_schema.dump(app_api), HTTPStatus.CREATED
    except ValidationError as e:
        current_app.running_context.execution_db.session.rollback()
        return improper_json_problem('app_api', 'create', app_name, e.messages)
    except IntegrityError:
        current_app.running_context.execution_db.session.rollback()
        return unique_constraint_problem('app_api', 'create', app_name)


# def extract_schema(api, unformatted_fields=('name', 'example', 'placeholder', 'description', 'required')):
#     ret = {}
#     schema = {}
#     for key, value in api.items():
#         if key not in unformatted_fields:
#             schema[key] = value
#         else:
#             ret[key] = value
#     ret['schema'] = schema
#     if 'schema' in ret['schema']:  # flatten the nested schema, happens when parameter is an object
#         ret['schema'].update({key: value for key, value in ret['schema'].pop('schema').items()})
#     return ret
#
#
# def format_returns(api, with_event=False):
#     ret_returns = []
#     for return_name, return_schema in api.items():
#         return_schema.update({'status': return_name})
#         ret_returns.append(return_schema)
#     ret_returns.extend(
#         [{'status': 'UnhandledException', 'failure': True, 'description': 'Exception occurred in action'},
#          {'status': 'InvalidInput', 'failure': True, 'description': 'Input into the action was invalid'}])
#     if with_event:
#         ret_returns.append(
#             {'status': 'EventTimedOut', 'failure': True, 'description': 'Action timed out out waiting for event'})
#     return ret_returns
#
#
# def format_app_action_api(api, app_name, action_type):
#     ret = deepcopy(api)
#     if 'returns' in api:
#         ret['returns'] = format_returns(ret['returns'], 'event' in api)
#     # if action_type in ('conditions', 'transforms') or not is_app_action_bound(app_name, api['run']):
#     #     ret['global'] = True
#     ret["global"] = True
#     if 'parameters' in api:
#         ret['parameters'] = [extract_schema(param_api) for param_api in ret['parameters']]
#     else:
#         ret['parameters'] = []
#     return ret
#
#
# def format_all_app_actions_api(api, app_name, action_type):
#     actions = []
#     for action_name, action_api in api.items():
#         ret_action_api = {'label': action_name}
#         ret_action_api.update(format_app_action_api(action_api, app_name, action_type))
#         actions.append(ret_action_api)
#     return sorted(actions, key=lambda action: action['label'])
#
#
# def format_device_api_full(api, device_name):
#     device_api = {'name': device_name}
#     unformatted_fields = ('name', 'description', 'encrypted', 'placeholder', 'required')
#     if 'description' in api:
#         device_api['description'] = api['description']
#     device_api['fields'] = [extract_schema(device_field,
#                                            unformatted_fields=unformatted_fields)
#                             for device_field in api['fields']]
#
#     return device_api
#
#
# def format_full_app_api(api, app_name):
#     ret = {'name': app_name}
#     for unformatted_field in ('info', 'tags', 'external_docs'):
#         if unformatted_field in api:
#             ret[unformatted_field] = api[unformatted_field]
#         else:
#             ret[unformatted_field] = [] if unformatted_field in ('tags', 'external_docs') else {}
#     for formatted_action_field in ('actions', 'conditions', 'transforms'):
#         if formatted_action_field in api:
#             ret[formatted_action_field[:-1] + '_apis'] = format_all_app_actions_api(api[formatted_action_field],
#                                                                                     app_name, formatted_action_field)
#         else:
#             ret[formatted_action_field[:-1] + '_apis'] = []
#     if 'devices' in api:
#         ret['device_apis'] = [format_device_api_full(device_api, device_name)
#                               for device_name, device_api in api['devices'].items()]
#     else:
#         ret['device_apis'] = []
#     return ret


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('app_apis', ['read']))
def read_all_app_apis():
    ret = []
    for app_api in current_app.running_context.execution_db.session.query(AppApi).order_by(AppApi.name).all():
        ret.append(remove_locations(app_api_schema.dump(app_api)))
    return ret, HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('app_apis', ['read']))
@with_app_api_name('read', 'app_name')
def read_app_api(app_name):
    return remove_locations(app_api_schema.dump(app_name)), HTTPStatus.OK


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('app_apis', ['update']))
@with_app_api_name('update', 'app_name')
def update_app_api(app_name):
    data = request.get_json()
    add_locations(data)
    try:
        app_api_schema.load(data, instance=app_name)
        current_app.running_context.execution_db.session.commit()
        current_app.logger.info(f"Updated app_api {app_name.name} ({app_name.id_})")
        return app_api_schema.dump(app_name), HTTPStatus.OK
    except IntegrityError:
        current_app.running_context.execution_db.session.rollback()
        return unique_constraint_problem('app_api', 'update', app_name.id_)


@jwt_required
@permissions_accepted_for_resources(ResourcePermissions('app_apis', ['delete']))
@with_app_api_name('delete', 'app_name')
def delete_app_api(app_name):
    current_app.running_context.execution_db.session.delete(app_name)
    current_app.logger.info(f"Removed app_api {app_name.name} ({app_name.id_})")
    current_app.running_context.execution_db.session.commit()
    return None, HTTPStatus.NO_CONTENT

# def read_app_api_field(app_name, field_name):
#     @jwt_required
#     @permissions_accepted_for_resources(ResourcePermissions('app_apis', ['read']))
#     def __func():
#         # TODO: Remove this once connexion can validate enums with openapi3.
#         if field_name not in ['info', 'action_apis', 'condition_apis', 'transform_apis', 'device_apis', 'tags',
#                               'externalDocs']:
#             return Problem(HTTPStatus.BAD_REQUEST, 'Could not read app api.',
#                            '{} is not a valid field name.'.format(field_name))
#
#         api = json.loads(redis_cache.hget("app-apis", app_name))
#         if api is not None:
#             return format_full_app_api(api, app_name)[field_name], HTTPStatus.OK
#         else:
#             return app_api_dne_problem(app_name)
#
#     return __func()
