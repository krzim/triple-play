import pytest

import api_gateway.server.endpoints.workflows

# def test_abort_workflow(api_gateway, workflow, execdb):

def test_workflow_exist(api_gateway, workflow, execdb):
	
	assert does_workflow_exist(workflow.id_) == True