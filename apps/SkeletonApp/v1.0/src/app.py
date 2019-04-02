import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase

class SkeletonApp(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
    
    def test_global_action(data):
    	return data

    def test_function(self):
    	"""
           Basic self contained function
        """
        return {}

    def test_function_with_param(self, test_param):
    	 """
           Basic function that takes in a parameter

           Args:
               test_param (str): String that will be returned
        """
        return test_param

     """

		removed Basic function that calls an instance variable.  In this case, a device name. 

		    @action
    def test_function_with_device_reference(self)
       
        # password = self.get_device().get_encrypted_field('password'); do not store this variable in cache
        return self.device_fields['username']


     """

if __name__ == "__main__":
    import argparse
    LOG_LEVELS = ("debug", "info", "error", "warn", "fatal", "DEBUG", "INFO", "ERROR", "WARN", "FATAL")
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", dest="log_level", choices=LOG_LEVELS, default="DEBUG")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format="{asctime} - {name} - {levelname}:{message}", style='{')
    logger = logging.getLogger("SkeletonApp")

    async def run():
        app = SkeletonApp(logger=logger)
        async with app.connect_to_redis_pool():
            await app.get_actions()

    asyncio.run(run())
