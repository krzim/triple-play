import pytest
import json
from api_gateway.extensions import db


@pytest.fixture(scope='function')
def api_gateway():
    from api_gateway.server.app import app
    from api_gateway.server.blueprints.root import create_user
    with app.app_context():
        create_user()
        app.testing = True
        api_gateway = app.test_client()
        yield api_gateway


@pytest.fixture(scope='function')
def token(api_gateway):
    header = {'content-type': "application/json"}
    response = api_gateway.post('/api/auth',
                                data=json.dumps(dict(username='admin', password='admin')), headers=header)
    token = json.loads(response.get_data(as_text=True))
    yield token


@pytest.fixture(scope='function')
def serverdb():
    yield db
    db.drop_all()


@pytest.fixture(scope='function')
def execdb():
    from api_gateway.server.app import app
    yield app.running_context.execution_db
    app.running_context.execution_db.drop_all()
