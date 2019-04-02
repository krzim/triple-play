import socket
import asyncio
import logging

import splunklib.client as client
from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Splunk(Appbase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
        
    def set_create_args(self, key, value, kwargs_create):
        temp = kwargs_create
        temp[key] = value
        return temp

    def set_results_args(self, key, value, kwargs_results):
        temp = kwargs_results
        temp[key] = value
        return temp

    def clear_create_args(self, kwargs_create):
        temp = kwargs_create
        temp.clear()
        return temp

    def clear_results_args(self, kwargs_results):
        temp = kwargs_results
        temp.clear()
        return temp

    def search(self, query, ip, port, username, password):
        kwargs_create = {}
        kwargs_results = {"output_mode": "json"}

        service = client.connect(host=ip, port=port, username=username, password=password)
        
        if not query.startswith('search'):
            query = "search " + query

        job = service.jobs.create(query, **kwargs_create)

        while True:
            while not job.is_ready():
                pass
            if job['isDone'] == '1':
                break

        res = job.results(**kwargs_results)

        results = res.read()

        job.cancel()

        return results

    def shutdown(self):
        return
