import psutil
import gevent
import json
from collections import namedtuple
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

threat_pid = namedtuple("thread_pid", ["threat_name", "threat_exe", "pid"])
suspicious_pids = []

class CyberAnalytic(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
    
    global suspicious_pids

    def __monitor_processes(self):
        while True:
            for proc in psutil.process_iter():
                if 'at.exe' in proc.exe():
                    suspicious_pids.append(threat_pid("at.exe", proc.name(), proc.pid))
                elif 'schtasks.exe' in proc.exe():
                    suspicious_pids.append(threat_pid("schtask.exe", proc.name(), proc.pid))
                elif 'cmd.exe' in proc.exe():
                    if proc.parent() and "explorer.exe" not in proc.parent().exe():
                        suspicious_pids.append(threat_pid("cmd.exe", proc.name(), proc.pid))

    def begin_monitoring(self):
        gevent.spawn(self.__monitor_processes)
        return "Success"

    def get_exe_pids(self):
        return json.dumps(suspicious_pids)


    def get_exe_pids_by_name(self, name):
        return [x for x in suspicious_pids if x.name == name]

