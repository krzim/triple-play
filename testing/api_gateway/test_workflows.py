import pytest

import api_gateway.server.endpoints.workflows
import json
import logging
# def test_abort_workflow(api_gateway, workflow, execdb):

def test_workflow_exist_post(api_gateway, token, execdb):
	header = {'Authorization': 'Bearer {}'.format(token['access_token'])}

	with open("testing/util/workflow.json") as fp:
		wf_json = json.load(fp)
		data = json.dumps(wf_json)

	response1 = api_gateway.post('/api/workflows', data=data, headers=header, content_type="application/json")
	assert response1.status_code == 201
	response2 = api_gateway.get('/api/workflows', data={"workflow_id": "e8c7840a-bd3e-4cfd-b9be-e07269b10c89"}, headers=header, content_type="application/json")
	key = json.loads(response2.get_data(as_text=True))

	response3 = api_gateway.delete('/api/workflows', data={"workflow_id": "e8c7840a-bd3e-4cfd-b9be-e07269b10c89"}, headers=header)
	assert response3.status_code == 204
	
