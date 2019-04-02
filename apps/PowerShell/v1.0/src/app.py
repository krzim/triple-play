import winrm
import subprocess
import chardet
import codecs
import logging
#from base64 import b64encodefrom datetime import datetime

import socket
import asyncio
import time

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")
#logger = logging.getLogger(__name__)

class PowerShell(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def set_options(transport, server_cert_validation, message_encryption, read_timeout_sec,
        operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, kerberos_delegation, 
        kerberos_hostname_override):
        options = {}
        if transport != "plaintext":
            options["transport"] = transport

        if server_cert_validation != "validate":
            options["server_cert_validation"] = server_cert_validation

        if message_encryption != "auto":
            options["message_encryption"] = message_encryption

        if read_timeout_sec not in (None, 30):
            options["read_timeout_sec"] = read_timeout_sec

        if operation_timeout_sec not in (None, 20):
            options["operation_timeout_sec"] = operation_timeout_sec

        if options.get("read_timeout_sec", 30) <= options.get("operation_timeout_sec", 20):
            options["read_timeout_sec"] = options.get("operation_timeout_sec", 20) + 10

        if keytab not in (None, ""):
            options["keytab"] = keytab

        if ca_trust_path not in (None, ""):
            options["ca_trust_path"] = ca_trust_path

        if cert_pem not in (None, ""):
            options["cert_pem"] = cert_pem

        if cert_key_pem not in (None, ""):
            options["cert_key_pem"] = cert_key_pem

        if kerberos_delegation:
            options["kerberos_delegation"] = True

        if kerberos_hostname_override not in (None, ""):
            options["kerberos_hostname_override"] = kerberos_hostname_override

        return options
        logger.info("Options: {}".format(self.options))
    
    def __process_command(self, session, host, command, results, out_dir, out_file, timestamp = None):
        if timestamp is None:
            timestamp = set_timestamp()

        try:
            rs = session.run_cmd(command)
        except Exception as e:
            logger.info(e)
            return results, "ScriptError"

        if not isinstance(rs.std_out, str) and len(rs.std_out) > 0:
            rs.std_out = rs.std_out.decode(chardet.detect(rs.std_out)["encoding"])
        if not isinstance(rs.std_err, str) and len(rs.std_err) > 0:
            rs.std_err = rs.std_err.decode(chardet.detect(rs.std_err)["encoding"])

        if rs.status_code == 0 and rs.std_out:
            results[host].append(rs.std_out.encode("utf-8"))
            status = "Success"
        else:
            results[host].append(rs.std_err.encode("utf-8"))
            status = "ScriptError"

        if all((out_file, out_dir)):
            try:
                host_dir = os.path.join(out_dir, host, timestamp)
                os.makedirs(host_dir, exist_ok=True)
                filepath = os.path.join(host_dir, out_file)
                with open(filepath, 'w') as f:
                    for result in results[host]:
                        f.write(result.replace(b"\r\n", b"\n").decode("utf-8"))
            except IOError as e:
                return e, "FileError"

        return results, status

    def set_timestamp(self):
        timestamp = '{:%Y-%m-%d_%H-%M-%S}'.format(datetime.utcnow())
        return timestamp

    def exec_local_command(self, platform, mode, commands, output_filename=None):
        """
        Execute PowerShell command locally, using either Windows PowerShell or cross-platform PowerShell Core if it is installed.
        :param platform: Whether to execute using Windows PowerShell or PowerShell Core
        :param mode: Whether to execute the following commands as cmdlets or script files
        :param commands: List of commands or scripts to execute
        :param output_filename: local path to output results into
        :return: list of results
        """
        results = []
        status = "Success"
        if platform == "PowerShell.exe (Windows)":
            executable = "powershell.exe"
        elif platform == "PowerShell Core (Cross-Platform)":
            executable = "pwsh"
        else:
            return "Unknown Platform", "ScriptError"

        for command in commands:
            try:
                if mode == "-Command":
                    args = [executable, mode, command]
                elif mode == "-File":
                    args = [executable, mode] + command.split(" ")
                results.append(subprocess.check_output(args))
            except subprocess.CalledProcessError as e:
                results.append(e.output)
                status = "ScriptError"
        if output_filename is not None:
            try:
                with open(output_filename, 'w') as f:
                    for result in results:
                        f.write(result)
            except IOError as e:
                return e, "FileError"

        return str(results), status

    def exec_remote_command(self, hosts, commands, username, password, transport, server_cert_validation, message_encryption, read_timeout_sec,
        operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, kerberos_delegation, 
        kerberos_hostname_override, output_directory=None, output_filename=None):
        """
        Execute a list of remote commands on a list of hosts.
        Outputs each host's file to a subdirectory of output_directory in output_filename
        :param hosts: list of hosts to execute on
        :param commands: list of commands to execute
        :param output_directory: directory to put output in
        :param output_filename: filename to put output in
        :return: dict of results with hosts as keys and list of outputs for each
        """
        options = set_options(transport, server_cert_validation, message_encryption, read_timeout_sec,
        operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, kerberos_delegation, 
        kerberos_hostname_override) 

        t = (output_filename, output_directory)
        if not (all(t) or not any(t)):
            return "Either both output_directory and output_filename must be set, or neither.", "ScriptError"

        results = {}
        status = "Success"

        for host in hosts:
            logger.info("Executing on {}".format(host))
            results[host] = []
            s = winrm.Session(host,
                              auth=(username, password),
                              **options)
            for command in commands:
                b64script = b64encode(command.encode('utf_16_le')).decode('ascii')
                cmd = "mode con: cols=1000 && powershell -encodedcommand {}".format(b64script)

                results, status = self.__process_command(s, host, cmd, results, output_directory, output_filename)
            logger.info("Done executing on {}".format(host))

        return str(results), status

    def exec_script_remotely(self, hosts, script_path, username, password, transport, server_cert_validation, 
        message_encryption, read_timeout_sec, operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, 
        kerberos_delegation, kerberos_hostname_override, output_directory=None, output_filename=None,tab_separated_values=False):
        """, 
        Load a .ps1 script from file and execute it on a list of hosts.
        Outputs each host's results to a subdirectory of output_directory in output_filename
        :param hosts:
        :param script_path: location of script to load
        :param output_directory: directory to put output in
        :param output_filename: filename to put output in
        :param tab_separated_values: whether to convert the script output to TSV
        :return: dict of results with hosts as keys and list of outputs for each
        """
        options = set_options(transport, server_cert_validation, message_encryption, read_timeout_sec,
        operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, kerberos_delegation, 
        kerberos_hostname_override)

        t = (output_filename, output_directory)
        if not (all(t) or not any(t)):
            return "Either both directory, filename, and tsv must be set, or neither.", "ScriptError"

        results = {}
        try:
            raw = open(script_path, 'rb').read()
            enc = chardet.detect(raw)['encoding']
            with codecs.open(script_path, 'r', encoding=enc) as f:
                script = f.read()
        except IOError as e:
            return e, "FileError"

        script = "$t = @'\n{}\n'@".format(script)
        script += ';Invoke-Expression $t'

        if tab_separated_values:
            script += '|ConvertTo-CSV -Delimiter "`t" -NoTypeInformation'
            script += '|% { $_ -replace "`"" }'

        b64script = b64encode(script.encode('utf_16_le')).decode('ascii')
        cmd = "mode con: cols=32766 && powershell -encodedcommand {}".format(b64script)

        status = "Success"
        for host in hosts:
            logger.info("Executing on {}".format(host))
            results[host] = []
            s = winrm.Session(host,
                              auth=(username, password),
                              **options)

            results, status = self.__process_command(s, host, cmd, results, output_directory, output_filename)

            logger.info("Done executing on {}".format(host))

        return str(results), status

    def compare_kbs(self, host_ips, req_kbs, username, password, transport, server_cert_validation, 
        message_encryption, read_timeout_sec, operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, 
        kerberos_delegation, kerberos_hostname_override,):
        """Parses the KBs on each Windows host and compares them to a list of required KBs
        :param host_ips: A list of IP addresses
        :param req_kbs: A filename corresponding to a file with a list of comma-separated required KBs
        :return: A list of objects for display with jstree
        """

        options = set_options(transport, server_cert_validation, message_encryption, read_timeout_sec,
        operation_timeout_sec, keytab, ca_trust_path, cert_pem, cert_key_pem, kerberos_delegation, 
        kerberos_hostname_override)

        kbs = set()
        for kb in req_kbs.split(","):
            kbs.add(kb.strip())

        host_missing_kbs = []
        for host in host_ips:
            logger.info("Executing on {}".format(host))
            s = winrm.Session(host, auth=(username, password),
                              **options)
            success = False
            for i in range(1, 3):
                try:
                    rs = s.run_cmd("wmic qfe list full")

                    if not isinstance(rs.std_out, str) and len(rs.std_out) > 0:
                        rs.std_out = rs.std_out.decode(chardet.detect(rs.std_out)["encoding"])
                    if not isinstance(rs.std_err, str) and len(rs.std_err) > 0:
                        rs.std_err = rs.std_err.decode(chardet.detect(rs.std_err)["encoding"])

                    installed_kbs = self.__parse_qfe_output(rs.std_out)

                    host_missing_kbs.append(self.__jstree_struct(host,
                                                                 list(installed_kbs & kbs),
                                                                 list(kbs - installed_kbs)))

                    # print(rs.std_out, rs.std_err, host_missing_kbs)
                    success = True
                except Exception as e:
                    logger.info(e)
                    # logger.info(rs.std_err)
                    continue
                else:
                    break
            if not success:
                host_missing_kbs.append({"text": host,
                                         "icon": "fa fa-desktop",
                                         "state": {"opened": True},
                                         "children": [
                                             {
                                                 "text": "Could not retrieve KBs from this host.",
                                                 "icon": "fa fa-times-circle-o"
                                             }
                                         ]})

            logger.info("Done executing on {}".format(host))

        return host_missing_kbs

    def __parse_qfe_output(cmd):
        kbs = set()
        for entry in cmd.split("\r\n\r\n"):
            fields = entry.split("\r\n")
            for field in fields:
                desc_val = field.split("=")
                if desc_val[0] == "HotFixID":
                    kbs.add(desc_val[1].strip())
        return kbs

    def __jstree_struct(host, comp, miss):
        return {
            "text": host,
            "icon": "fa fa-desktop",
            "state": {"opened": True},
            "children": [
                {
                    "text": "compliant",
                    "icon": "fa fa-check-circle-o",
                    "state": {"opened": True},
                    "children": [{"text": i, "icon": "fa fa-cubes", "li_attr": {"style": "color: green"}} for i in comp]
                },
                {
                    "text": "missing",
                    "icon": "fa fa-times-circle-o",
                    "state": {"opened": True},
                    "children": [{"text": i, "icon": "fa fa-cubes", "li_attr": {"style": "color: red"}} for i in miss]
                }
            ]
        }

if __name__ == "__main__":
    import argparse
    LOG_LEVELS = ("debug", "info", "error", "warn", "fatal", "DEBUG", "INFO", "ERROR", "WARN", "FATAL")
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", dest="log_level", choices=LOG_LEVELS, default="DEBUG")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format="{asctime} - {name} - {levelname}: {message}", style='{')
    logger = logging.getLogger("PowerShell")

    app = PowerShell();
    answer = app.exec_local_command("PowerShell Core (Cross-Platform)", "-Command", ["Get-Random"])
    print(answer)

    # async def run():
    #     app = PowerShell(logger=logger)
    #     async with app.connect_to_redis_pool():
    #         await app.get_actions()

    # asyncio.run(run())