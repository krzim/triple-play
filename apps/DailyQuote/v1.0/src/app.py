import requests
import json
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

# There is an associated Daily Quote test workflow which can be executed

class DailyQuote(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    # Returns the message defined in init above
    def quoteIntro(self):
        introMessage = {"message": "Quote App"}
        return introMessage

    def repeatBackToMe(self, call):
        return "REPEATING: " + call

    # Uses argument passed to function to make an api request
    def forismaticQuote(self, url):
        headers = {'content-type': 'application/json'}
        payload = {'method': 'getQuote', 'format': 'json', 'lang': 'en'}
        s = requests.Session()
        result = s.get(url, params=payload, verify=False)
        try:
            json_result = json.loads(result.text)
            json_result['success'] = True
            return json_result
        except:
            return {'success': False, 'text': result.text}

    # Uses the url defined in _init to make a getQuote api call and returns the quote
    def getQuote(self):
        headers = {'content-type': 'application/json'}
        url = "http://quotes.rest/qod.json?category=inspire"
        s = requests.Session()
        result = s.get(url, headers=headers, verify=False)
        return result.json()

    def shutdown(self):
        return
