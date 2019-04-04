import pytest

import api_gateway.server.endpoints.workflows
import json
import logging
# def test_abort_workflow(api_gateway, workflow, execdb):

def test_workflow_exist_post(api_gateway, token, workflow, execdb):
	header = {'Authorization': 'Bearer {}'.format(token['access_token'])}
	SUCCESS = 200
	with open("testing/util/workflow.json") as fp:
		wf_json = json.load(fp)
		data = json.dumps(wf_json)
	
	response = api_gateway.post('/api/workflows', data=data, headers=header, content_type="application/json")
	assert response.status_code == SUCCESS