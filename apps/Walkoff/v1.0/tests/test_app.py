from apps.Walkoff.v1_0.src.app import Walkoff
import pytest 
import asyncio

@pytest.mark.asyncio
async def test_connect():
	app = Walkoff()
	timeout = 2
	username = 'admin'
	password = 'admin'
	#admin_login = await ((await app.connect(timeout, username, password))[0]).json()
	success_or_failure = (await app.connect(timeout, username, password))[1]
	admin_login = await (await app.connect(timeout, username, password))[0].json()
	assert success_or_failure == 'Success'
	return app, admin_login, timeout

@pytest.mark.asyncio
async def test_disconnect():
	#dependent on test_connect working 
	app, admin_login, timeout = await test_connect()
	refresh_token = admin_login['refresh_token']
	admin_logout = await app.disconnect(timeout, refresh_token)
	assert admin_logout == 'Success'

@pytest.mark.asyncio
async def test_app_metrics():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	metrics = await app.get_app_metrics(timeout, access_token)
	assert metrics[1] == 'Success'

@pytest.mark.asyncio
async def test_workflow_metrics():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	metrics = await app.get_workflow_metrics(timeout, access_token)
	assert metrics[1] == 'Success'

@pytest.mark.asyncio
async def test_get_all_users():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	users = await app.get_all_users(timeout, access_token)
	assert users[1] == 'Success'

@pytest.mark.asyncio
async def test_get_all_workflows():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	workflows = await app.get_all_workflows(timeout, access_token)
	assert workflows[1] == 'Success'

@pytest.mark.asyncio
async def test_get_workflow_id():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	info = await app.get_all_workflows(timeout, access_token)
	playbook_name = info[0][0]['name']
	workflow_name = info[0][0]['workflows'][0]['name']
	result = await app.get_workflow_id(playbook_name, workflow_name, timeout, access_token)
	assert result[1] == 'Success'
	return result[0]

@pytest.mark.asyncio
async def test_execute():
	#assumes user has at least 1 playbook with at least 1 action
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	workflow_id = await test_get_workflow_id()
	result = await app.execute_workflow(workflow_id, timeout, access_token)
	assert result[1] == 'Success'
	return result[0]

# def test_resume():
# 	# execution_id = test_execute()
# 	# app, admin_login, timeout = test_connect()
# 	# access_token = admin_login[0]['access_token']
# 	# result = app.resume_workflow(execution_id, timeout, access_token)
# 	return "Pushed off to v1.1"

# def test_pause():
# 	# app, admin_login, timeout = test_connect()
# 	# access_token = admin_login[0]['access_token']
# 	# execution_id = test_execute()
# 	# result = app.pause_workflow(execution_id, timeout, access_token)
# 	return "Pushed off to v1.1"

# def test_trigger():
# 	return "Pushed off to v1.1"

@pytest.mark.asyncio
async def test_get_workflow_results():
	app, admin_login, timeout = await test_connect()
	access_token = admin_login['access_token']
	result = await app.get_workflow_results(timeout, access_token)
	assert result[1] == 'Success'

def test_wait_for_workflow_completion():
	# execution_id = test_execute()
	# app, admin_login, timeout = test_connect()
	# access_token = admin_login[0]['access_token']
	# assert app.wait_for_workflow_completion(execution_id, 2, 1, 1, access_token) == 'Success'
	return "idk how to write a test for this"

