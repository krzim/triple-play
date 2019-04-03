from api_gateway.server.endpoints.appapi import read_all_apps, extract_schema, format_returns, format_app_action_api, \
    format_all_app_actions_api, format_device_api_full, format_full_app_api, read_all_app_apis, app_api_dne_problem, \
    read_app_api, read_app_api_field
import pytest
import asyncio

from async_generator import yield_, async_generator
import birdisle.aioredis


from apps.HelloWorld.v1_0.src.app import HelloWorld
from common.workflow_types import workflow_load, Node, Action, Condition, Transform, Trigger, ParameterVariant, \
    Workflow, workflow_dumps, workflow_loads, workflow_dump, ConditionException


@pytest.fixture
@async_generator
async def redis(server):
    redis = await birdisle.aioredis.create_redis(server)
    await yield_(redis)
    redis.close()
    await redis.wait_closed()


@pytest.mark.asyncio
async def test_read_apps(redis):
    app = HelloWorld()
    #app =
    #redis.lpush(app, )

    timeout = 2
    username = 'admin'
    password = 'admin'
    # admin_login = await ((await app.connect(timeout, username, password))[0]).json()
    # success_or_failure = (await app.connect(timeout, username, password))[1]
    # admin_login = await ((await app.connect(timeout, username, password))[0]).json()
    assert success_or_failure == 'Success'
    return app, admin_login, timeout
