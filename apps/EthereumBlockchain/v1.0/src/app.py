import os, subprocess, signal
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class EthereumBlockchain(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)
        
    def create_accounts(self, total_nodes):
        res = 0
        # self.totalNodes = total_nodes

        self.terminate_geth_processes()
        res &= self._run_script(["step1-create-accounts.sh", total_nodes])
        return res

    def set_up_network(self, total_nodes):
        res = 0
        res &= self._run_script(["step2-create-genesis-file.sh"])
        res &= self._run_script(["step3-start-miners.sh"])
        res &= self._run_script(["step4-connect-miners.sh", total_nodes])
        res &= self._run_script(["step5-deploy-contract.sh", total_nodes])
        return res

    def submit_greeting(self, greeting):
        return self._run_script(["step6-submit-greeting.sh", greeting])

    def _run_script(self, args=[]):
        curDirPath = os.path.dirname(os.path.realpath(__file__))
        args[0] = curDirPath + "/" + args[0] # Full path to the script file
        args.insert(1, curDirPath) # Full path to the Ethereum Blockchain directory
        process = subprocess.Popen(args)
        return process.wait()

    def terminate_geth_processes(self):
        process_name = "geth"
        ps_cmd = subprocess.Popen("ps -A", shell=True, stdout=subprocess.PIPE)
        grep_cmd = subprocess.Popen("grep " + process_name, shell=True, stdin=ps_cmd.stdout, stdout=subprocess.PIPE)
        out, err = grep_cmd.communicate()
        for line in out.splitlines():
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)
        return "Success"
