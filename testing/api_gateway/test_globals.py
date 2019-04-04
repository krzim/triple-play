import json
import requests
import logging
from api_gateway.server.app import app


logger = logging.getLogger(__name__)


def test_create_global(api_gateway, token, serverdb, execdb):
    headers = {'Authorization': 'Bearer {}'.format(token['access_token']), 'content-type': 'application/json'}
    add_global = api_gateway.post('/api/globals',
                                  data=json.dumps({'description': 'foo', 'name': 'admin', 'value': 'bar'}),
                                  headers=headers)
    key1 = json.loads(add_global.get_data(as_text=True))
    rec_globals = api_gateway.get('/api/globals', headers=headers)
    key2 = json.loads(rec_globals.get_data(as_text=True))

    assert key1['description'] == key2[0]['description']
    assert key1['name'] == key2[0]['name']
    assert key1['value'] == key2[0]['value']


def test_read_all_globals_in_db(api_gateway, token, serverdb, execdb):
    header = {'Authorization': 'Bearer {}'.format(token['access_token']), 'content-type': 'application/json'}
    response = api_gateway.get("/api/globals", headers=header)
    key = json.loads(response.get_data(as_text=True))
    assert response.status_code == 200
    assert key == []
