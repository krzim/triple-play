import pytest
import json
import requests
import logging
from api_gateway.server.app import app
from flask_jwt_extended import decode_token, JWTManager
from api_gateway.config import Config
from api_gateway.serverdb.user import User
from api_gateway.serverdb.role import Role
from api_gateway.serverdb.tokens import BlacklistedToken
from api_gateway.serverdb import add_user

logger = logging.getLogger(__name__)


def test_create_global(api_gateway, token, serverdb):

    headers = {'Authorization': 'Bearer {}'.format(token['access_token']), 'content-type': 'application/json'}
    add_global = api_gateway.post('/api/globals',
                                  data=json.dumps({'description': 'foo', 'name': 'admin', 'value': 'bar'}),
                                  headers=headers)
    key1 = json.loads(add_global.get_data(as_text=True))
    rec_globals = api_gateway.get('/api/globals', headers=headers)
    key2 = json.loads(rec_globals.get_data(as_text=True))

    assert key1['description'] == key2[1]['description']
    assert key1['name'] == key2[1]['name']
    assert key1['value'] == key2[1]['value']



