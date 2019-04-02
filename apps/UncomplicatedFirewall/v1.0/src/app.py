import subprocess
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class UncomplicatedFirewall(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def execute_command(self, cmd):
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            return {'error': e.output, 'code': e.returncode}, 'Failure'
        else:
            return output


    def enable(self):
        """
           Basic self contained function
        """
        return execute_command(['ufw', 'enable'])


    def disable(self):
        """
           Basic self contained function
        """
        return execute_command(['ufw', 'disable'])


    def status(self, verbose=False):
        """
           Basic function that takes in a parameter

           Args:
               verbose (bool): Should output be verbose? Defaults to False
        """
        command = ['ufw', 'status'] if not verbose else ['ufw', 'status', 'verbose']
        return execute_command(command)


    def allow(self, port, from_address='any', to_address='any', protocol='any', comment=None):
        command = (['ufw', 'allow', 'from', from_address, 'to', to_address, 'port', port, 'proto', protocol])
        if comment:
            command.extend(['comment', comment])
        return execute_command(command)


    def allow_service(self, service):
        command = ['ufw', 'allow', service]
        return execute_command(command)


    def deny(self, from_address, protocol='any', port=None, comment=None):
        command = ['ufw', 'deny', 'from', from_address, 'to', protocol]
        if port:
            command.extend(['port', port])
        if comment:
            command.extend(['comment', comment])
        return execute_command(command)
