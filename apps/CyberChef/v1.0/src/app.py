import logging
import json
import tempfile
import shutil
import os
from Naked.toolshed.shell import muterun_js
import socket
import asyncio
import time

from app_sdk.app_base import AppBase
logger = logging.getLogger(__name__)

class CyberChefApp(AppBase):
    """
       Runs operations from GCHQ Cyberchef
       https://github.com/gchq/CyberChef

       Args:
           name (str): Name of the app
           device (list[str]): List of associated device names

    """
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def setupOpTemporaryCopy(self, value, action, args, cyberchefpath):
        operationsScript = """
            p1 = module.exports.bake("{0}", [{{ "op":"{1}","args":{2} }}] );
            Promise.all([p1]).then(values => {{
                console.log(JSON.stringify(values[0]));
            }});
        """.format(value, action, args)
        temppath = os.path.dirname(cyberchefpath)
        tf = tempfile.NamedTemporaryFile(mode="r+b", dir=temppath, prefix="__", suffix=".tmp")
        with open(cyberchefpath, "r+b") as f:
            shutil.copyfileobj(f, tf)

        tf.write(operationsScript.encode())
        # Rewind to beginning, otherwise Windows errors
        tf.seek(0)
        return tf

    def setupWorkflowTemporaryCopy(self, value, workflow, cyberchefpath):
        workflowScript = """
            p1 = module.exports.bake("{0}", {1} );
            Promise.all([p1]).then(values => {{
                console.log(JSON.stringify(values[0]));
            }});
        """.format(value, workflow)
        temppath = os.path.dirname(cyberchefpath)
        tf = tempfile.NamedTemporaryFile(mode="r+b", dir=temppath, prefix="__", suffix=".tmp")
        with open(cyberchefpath, "r+b") as f:
            shutil.copyfileobj(f, tf)

        tf.write(workflowScript.encode())
        # Rewind to beginning, otherwise Windows errors
        tf.seek(0)
        return tf

    def handleOutput(self, response):
        if response.exitcode == 0:
            r = json.loads(response.stdout.decode())
            #If the script executed but the workflow failed
            if r["error"] ==  True:
                return response.stdout, "Error"

            result = r["result"]
            if r["type"] == "number":
                result = float(result)
                return result, "SuccessNumber"
            return result, "Success"
        else:
            #If the script failed to execute
            return response.stderr, "Error"

    def run_cyberchef_function(self, input, action, args, cyberchefpath):
        #Javascript that ties together the execution

        with self.setupOpTemporaryCopy(input, action, args, cyberchefpath) as tf:
            response = muterun_js(tf.name)

        return self.handleOutput(response)


    def run_cyberchef_workflow(self, input, workflow, cyberchefpath):
        with self.setupWorkflowTemporaryCopy(input, workflow, cyberchefpath) as tf:
            response = muterun_js(tf.name)

        return self.handleOutput(response)

    def shutdown(self):
        pass



