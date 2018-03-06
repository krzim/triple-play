from flask_jwt_extended import jwt_required

from walkoff.security import permissions_accepted_for_resources, ResourcePermissions
from walkoff.server.returncodes import *


def read_app_metrics():
    @jwt_required
    @permissions_accepted_for_resources(ResourcePermissions('metrics', ['read']))
    def __func():
        return _convert_action_time_averages(), SUCCESS

    return __func()


def read_workflow_metrics():
    @jwt_required
    @permissions_accepted_for_resources(ResourcePermissions('metrics', ['read']))
    def __func():
        return _convert_workflow_time_averages(), SUCCESS

    return __func()


def _convert_action_time_averages():
    import walkoff.server.metrics as metrics
    apps_json = []
    for app_name, app in metrics.app_metrics.items():
        app_json = {"name": app_name, "count": app['count']}
        actions = []
        for action_name, action in app['actions'].items():
            action_json = {"name": action_name}
            if 'success' in action:
                action_json["success_metrics"] = {"count": action['success']['count'],
                                                  "avg_time": str(action['success']['avg_time'])}
            if 'error' in action:
                action_json["error_metrics"] = {"count": action['error']['count'],
                                                "avg_time": str(action['error']['avg_time'])}
            actions.append(action_json)
        app_json["actions"] = actions
        apps_json.append(app_json)
    return {"apps": apps_json}


def _convert_workflow_time_averages():
    import walkoff.server.metrics as metrics
    return {"workflows": [{"name": workflow_name,
                           "count": workflow["count"],
                           "avg_time": str(workflow["avg_time"])}
                          for workflow_name, workflow in metrics.workflow_metrics.items()]}
