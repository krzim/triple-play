import socket

from apps.HelloWorld.v1_0.src.app import HelloWorld
from apps.HelloWorld.v1_0.src.asyncio_practice import stream_of_consciousness
import pytest 
from unittest.mock import patch, ANY
from asynctest import CoroutineMock

# def test_hello_world():
# 	app = HelloWorld()
# 	assert app.hello_world() == "hi"
def test_hello_world():
	app = HelloWorld()
	message = app.hello_world()
	host = socket.gethostname()
	assert message['message'] == 'HELLO WORLD FROM ' + host

def test_repeat():
	app = HelloWorld()
	message = app.repeat_back_to_me("testing repeat")
	assert message == 'REPEATING: testing repeat'

def test_plus_one():
	app = HelloWorld()
	assert app.return_plus_one(2) == 3
	assert app.return_plus_one(-1) == 0
	assert app.return_plus_one(-3) == -2
	assert app.return_plus_one(2000) == 2001

def test_pause():
	app = HelloWorld()
	#part 1: test time paused
	#part 2: test output
	assert app.pause(2) == 2

def test_shutdown():
	app = HelloWorld()
	assert app.shutdown() is None

# #regular pytest testing async function
# @pytest.mark.asyncio
# async def test_async():
# 	app = HelloWorld()
# 	assert (await (app.hello(1)))[1] == 3

# fun pytest with a mock
@pytest.mark.asyncio
async def test_mock():
	sentences = ['a', 'b']
	assert (await (stream_of_consciousness(sentences))) == 3
# async def test_async():
# 	with 
