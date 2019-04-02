import pytest
import json
import requests
import logging
from api_gateway.server.app import app
from flask_jwt_extended import decode_token, JWTManager
from api_gateway.config import Config
from api_gateway.serverdb.user import User
from api_gateway.serverdb.role import Role
from api_gateway.serverdb import add_user
from api_gateway.extensions import db
import birdisle
from async_generator import yield_
logger = logging.getLogger(__name__)

@pytest.fixture(scope='function')
def client():
    from api_gateway.server.app import app
    app.testing = True
    client = app.test_client()
    yield client

def test_login_has_correct_return_code(client):
    SUCCESS = 201
    header = {'content-type': 'application/json'}
    response = client.post('/api/auth',
                           data=json.dumps(dict(username='admin', password='admin')), headers=header)
    assert response.status_code == SUCCESS

def test_login_has_correct_structure(client):
    SUCCESS = {'access_token', 'refresh_token'}
    header = {'content-type': 'application/json'}
    response = client.post('/api/auth',
                           data=json.dumps(dict(username='admin', password='admin')), headers=header)
    key = json.loads(response.get_data(as_text=True))
    assert set(key.keys()) == SUCCESS

def test_login_has_valid_access_token(client):
    header = {'content-type': 'application/json'}
    response = client.post('/api/auth',
                           data=json.dumps(dict(username='admin', password='admin')), headers=header)
    keys = json.loads(response.get_data(as_text=True))
    print(keys['access_token'])
    with app.app_context():
        token = decode_token(keys['access_token'])
        uid = db.session.query(User).filter_by(username='admin').first().id
        rid = db.session.query(Role).filter_by(name="admin").first().id
    SUCCESS = {'username': 'admin', 'roles': [rid]}
    assert token['type'] == 'access'
    # assert token['fresh'] == True
    assert token['identity'] == uid
    assert token['user_claims'] == SUCCESS

def test_login_has_valid_refresh_token(client):
    header = {'content-type': 'application/json'}
    response = client.post('/api/auth',
                           data=json.dumps(dict(username='admin', password='admin')), headers=header)
    keys = json.loads(response.get_data(as_text=True))
    with app.app_context():
        token = decode_token(keys['refresh_token'])
        uid = db.session.query(User).filter_by(username='admin').first().id
    assert token['type'] == 'refresh'
    assert token['identity'] == uid

def test_login_updates_user(client):
    uname = "newestuser2"
    with app.app_context():
        try:
            before = db.session.query(User).filter_by(username=uname).first().login_count
        except:
            before = 0
        user = add_user(username=uname, password='test')
        header = {'content-type': 'application/json'}
        client.post('/api/auth',
                    data=json.dumps(dict(username=uname, password='test')), headers=header)
        check = db.session.query(User).filter_by(username=uname).first().login_count
        assert check == before + 1

def test_login_auth_invalid_password(client):
    FAILURE = 401
    header = {'content-type': 'application/json'}
    response = client.post('/api/auth',
                           data=json.dumps(dict(username="invalid", password='admin')), headers=header)
    assert response.status_code == FAILURE