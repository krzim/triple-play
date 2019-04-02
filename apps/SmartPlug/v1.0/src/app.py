from pyHS100 import SmartPlug
import logging
try:
    import win_inet_pton
except ImportError:
    import os
    if os.name == 'nt':
        logging.getLogger(__name__).error('SmartPlug requires the win_inet_pton package to run on Windows. '
                                          'You can install using pip with "pip install win_inet_pton"')
import socket
import asyncio
import time

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class SmartPlug(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
    
    def get_state(self, ip):
        plug = SmartPlug(ip)
        return self.plug.state

    def turn_on(self, ip):
        plug = SmartPlug(ip)
        self.plug.turn_on()

    def turn_off(self, ip):
        plug = SmartPlug(ip)
        self.plug.turn_off()

    def on_since(self, ip):
        plug = SmartPlug(ip)
        return self.plug.on_since

    def shutdown(self):
        return
