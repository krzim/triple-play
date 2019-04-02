import pytest 

import os.path
from importlib import import_module
from unittest import TestCase

from api_gateway.appgateway.apiutil import UnknownApp, UnknownAppAction
from api_gateway.appgateway.appcache import AppCache

from async_generator import yield_, async_generator
import birdisle.redis


@pytest.fixture
def server():
    server = birdisle.Server()
    yield server
    server.close()

@pytest.fixture
def redis(server):
    redis = birdisle.redis.StrictRedis(server=server)
    yield redis

@pytest.fixture
def cache(redis):
    appCache = AppCache(redis)
    yield appCache

def test_init(redis, cache):
    assert cache.redis == redis
    assert cache.api_key == "app-apis"

def test_items(cache):
    cache.clear()
    assert