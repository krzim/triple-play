import paramiko, socket, os
import json
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class SSH(AppBase):
    """
    Initialize the Linux Shell App, which includes initializing the SSH client given the IP address, port, username, and
    password for the remote server
    """
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def exec_command(self, args, ip, port, username, password):
        """ Use SSH client to execute commands on the remote server and produce an array of command outputs
        Input:
            args: A string array of commands
        Output:
            result: A String array of the command outputs
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)

        result = []
        for cmd in args:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read()
            result.append(output)
        return str(result), 'Success'

    def sftp_put(self, local_path, remote_path, ip, port, username, password):
        """
        Use SSH client to copy a local file to the remote server using sftp
        Input:
            args: local_path and remote_path of file
        Output:
            Success/Failure
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)

        sftp = ssh.open_sftp()
        result = sftp.put(local_path, remote_path)
        sftp.close()
        return str(result), 'Success'

    def sftp_get(self, remote_path, local_path, ip, port, username, password):
        """
        Use SSH client to copy a remote file to local using sftp
        Input:
            args: local_path and remote_path of file
        Output:
            Success/Failure
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)

        sftp = ssh.open_sftp()
        result = sftp.get(local_path, remote_path)
        sftp.close()
        return str(result), 'Success'

    def run_shell_script_remotely(self, local_path, ip, port, username, password):
        """ Use SSH client to execute a shell script on the remote server and produce an array of command outputs
        Input:
            args: local filepath of the shell script
        Output:
            result: A String array of the command outputs
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)

        result = []
        script = open(local_path, "r").read()
        cmd = "eval " + script
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read()
        result.append(output)
        return str(result), 'Success'

    def shutdown(self, ip, port, username, password):
        """
        Close the SSH connection if there is a SSH connection
        """
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username, password)

        ssh.connect(ip, port, username, password)
        if ssh:
            print("SSH Connection Closed")
            ssh.close()
        return True, 'Success'
