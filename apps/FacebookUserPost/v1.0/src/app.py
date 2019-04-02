import requests
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")


class FacebookUserPost(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def post_to_user_wall(self, message, username, token):
        msg = message.replace(" ", "+")
        url = ('https://graph.facebook.com/v2.9/' + userid + '/feed?'
               'message=' + msg + '&access_token=' + token)
        return (requests.post(url, verify=False)).text
