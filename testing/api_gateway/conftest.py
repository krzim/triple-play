import pytest
from api_gateway.extensions import db
from api_gateway.server.app import app
from api_gateway.server.blueprints.root import create_user
import json
import aioredis
import asyncio
import aiohttp
from async_generator import yield_, async_generator
import birdisle.aioredis
from common.config import config
from common.workflow_types import workflow_load

@pytest.fixture
@async_generator
async def server(scope='function'):
    server = birdisle.Server()
    await yield_(server)
    server.close()


@pytest.fixture
def workflow():
    with open("testing/util/workflow.json") as fp:
        workflow = workflow_load(fp)
    yield workflow


@pytest.fixture
@async_generator
async def redis(server, scope='function'):
    redis = await birdisle.aioredis.create_redis(server)
    with open("testing/util/workflow.json") as fp:
        wf_json = json.load(fp)
        await redis.lpush(config["REDIS"]["workflow_q"], json.dumps(wf_json))
    await yield_(redis)
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='function')
def token(api_gateway):
    header = {'content-type': "application/json"}
    response = api_gateway.post('/api/auth',
                                data=json.dumps(dict(username='admin', password='admin')), headers=header)
    token = json.loads(response.get_data(as_text=True))
    yield token


@pytest.fixture(scope='function')
def api_gateway():
    with app.app_context():
        create_user()
        app.testing = True
        api_gateway = app.test_client()
        yield api_gateway


@pytest.fixture(scope='function')
def serverdb():
    yield db
    db.drop_all()


@pytest.fixture(scope='function')
def execdb():
    yield app.running_context.execution_db
    app.running_context.execution_db.drop_all()