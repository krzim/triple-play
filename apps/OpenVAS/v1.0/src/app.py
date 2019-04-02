import logging
from apps import App, action
from apps.OpenVAS.pvsl import Client, exceptions
from datetime import datetime
import csv
from tzlocal import get_localzone
import subprocess
import json
import socket
import asyncio

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")
# from apps.OpenVAS.events import pull_down


class OpenVAS(AppBase):
    """
       An app to interface with a running OpenVAS manager.
    """
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def app_create_port_list(self, name, port_range, host, username, password, port, comment=None):
        """
        Create a port list from range(s) of ports
        :param name: Name of the port range
        :param port_range: Port range (comma separated values, e.g. T:100-200,T:300-400,U:800-900
        :param comment: (Optional) Comment to add
        :return: uuid of the created list
        """
        try:
            with Client(host, username, password, port) as cli:
                r = cli.create_port_list(name, port_range=port_range, comment=comment)
                return r.data['@id']
        except exceptions.HTTPError:
            return False, "BadPorts"
        except exceptions.ElementExists:
            return False, "AlreadyExists"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_create_target(self, name, hosts, host, username, password, port, port_list=None, comment=None):
        """
        Creates a new target
        :param name: Name of the new target
        :param hosts: Comma separated list of hosts
        :param port_list: (Optional) uuid of the port list to use
        :param comment: (Optional) Comment to add
        :return: uuid of the created target
        """
        try:
            with Client(host, username, password, port) as cli:
                r = cli.create_target(name, hosts, port_list=port_list, comment=comment)
                return r.data['@id']
        except exceptions.ElementNotFound:
            return False, "InvalidUUID"
        except exceptions.ElementExists:
            return False, "AlreadyExists"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_create_schedule(self, name,  host, username, password, port, comment=None, first_time=None, local_server_time=False, duration=None,
                            duration_unit=None, period=None,
                            period_unit=None):
        """
        Creates a new schedule
        :param name: Name of the schedule
        :param comment: (Optional) Comment to add
        :param first_time: (Optional) First time to run the task, in the format "MM/DD/YYYY HH:MM _M" (12h)
        :param duration: (Optional) How long to run task before it is aborted
        :param duration_unit: (Optional) Units for duration
        :param period: (Optional) How often to run the task
        :param period_unit: (Optional) Units for period
        :param local_server_time: (Optional) UTC offset for local time in the format "+1:00" or "-1:00"
        :return: uuid of created schedule
        """

        time_json = None
        local_zone = None
        if first_time is not None:
            try:
                dt = datetime.strptime(first_time, '%m/%d/%Y %I:%M %p')

                if local_server_time is not False:
                    local_zone = get_localzone().zone

                time_json = {
                    "minute": dt.minute,
                    "hour": dt.hour,
                    "day_of_month": dt.day,
                    "month": dt.month,
                    "year": dt.year
                }
            except ValueError:
                return False, "BadTime"

        if ((duration is not None) ^ (duration_unit is not None)) or ((period is not None) ^ (period_unit is not None)):
            return False, "BadTime"

        if not self.valid_num(duration) or not self.valid_num(period):
            return False, "BadTime"

        try:
            with Client(host, username, password, port) as cli:
                r = cli.create_schedule(name, comment=comment, first_time=time_json, duration=duration,
                                        duration_unit=duration_unit, period=period, period_unit=period_unit,
                                        timezone=local_zone)
                return r.data['@id']
        except exceptions.ElementExists:
            return False, "AlreadyExists"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    # def app_create_http_alert_on_finish(self, name, url, comment=None):
    #     """
    #     Creates an HTTP GET alert that fires when a task is finished
    #     :param name: Name of the new alert
    #     :param url: URL to send an HTTP GET request to
    #     :param comment: (Optional) Comment to add
    #     :return: uuid of the created alert
    #     """
    #     try:
    #         with Client(self.h, username=self.u, password=self.device.get_encrypted_field('password'),
    #                     port=self.p) as cli:
    #             r = cli.create_http_alert_when_finished(name, url, comment=comment)
    #             return r.data['@id']
    #     except exceptions.ElementExists:
    #         return False, "AlreadyExists"
    #     except exceptions.AuthenticationError:
    #         return False, "AuthError"
    #     except IOError:
    #         return False, "ConnectError"

    def app_create_task(self, name, target_uuid, host, username, password, port, config_uuid='daba56c8-73ec-11df-a475-002264764cea', scanner_uuid=None,
                        comment=None, schedule_uuid=None, alert_uuid=None):
        """
        Creates a new task
        :param name: Name of the task
        :param config_uuid: uuid of the config to use
        :param target_uuid: uuid of the target to scan
        :param scanner_uuid: (Optional) uuid of the scanner to use
        :param comment: (Optional) Comment to add
        :param schedule_uuid: (Optional) uuid of the schedule to use
        :return: uuid of the created task
        """
        try:
            with Client(host, username, password, port) as cli:
                r = cli.create_task(name, config_uuid, target_uuid, scanner_uuid=scanner_uuid, comment=comment,
                                    schedule_uuid=schedule_uuid, alert_uuid=alert_uuid)
                return r.data['@id']
        except exceptions.ElementNotFound:
            return False, "InvalidUUID"
        except exceptions.ElementExists:
            return False, "AlreadyExists"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_start_task(self, uuid, host, username, password, port):
        """
        Starts the specified task
        :param uuid: uuid of task to execute
        :return: report uuid for this run
        """
        try:
            with Client(host, username, password, port) as cli:
                r = cli.start_task(uuid)
                return r.data['report_id']
        except exceptions.ElementNotFound:
            return False, "InvalidUUID"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_port_lists(self, host, username, password, port, name=None):
        """
        Lists all defined port lists
        :param name: (Optional) Name to search for
        :return: List of matching port lists
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_port_lists(name=name)
                else:
                    r = cli.list_port_lists()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_targets(self, host, username, password, port, name=None):
        """
        Lists all defined targets
        :param name: (Optional) Name to search for
        :return: List of matching targets
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_targets(name=name)
                else:
                    r = cli.list_targets()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_configs(self, host, username, password, port, name=None):
        """
        Lists all defined configs
        :param name: (Optional) Name to search for
        :return: List of matching targets
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_configs(name=name)
                else:
                    r = cli.list_configs()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_scanners(self, host, username, password, port, name=None):
        """
        Lists all defined scanners
        :param name: (Optional) Name to search for
        :return: List of matching targets
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_scanners(name=name)
                else:
                    r = cli.list_scanners()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_schedules(self, host, username, password, port, name=None):
        """
        Lists all defined schedules
        :param name: (Optional) Name to search for
        :return: List of matching schedules
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_schedules(name=name)
                else:
                    r = cli.list_schedules()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_tasks(self, host, username, poassword, port, name=None):
        """
        Lists all defined tasks
        :param name: (Optional) Name to search for
        :return: List of matching tasks
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_tasks(name=name)
                else:
                    r = cli.list_tasks()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_list_reports(self, host, username, password, port, name=None):
        """
        Lists all defined reports
        :param name: (Optional) Name to search for
        :return: List of matching reports
        """
        try:
            with Client(host, username, password, port) as cli:
                if name is not None:
                    r = cli.list_reports(name=name)
                else:
                    r = cli.list_reports()
                return r.data
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def app_download_report_as_xml(self, uuid, filename, host, username, password, port):
        """
        Gets report by uuid, then writes to filename
        :param uuid: uuid of report to get
        :param filename: filename to write to
        :return:
        """
        try:
            with Client(host, username, password, port) as cli:
                r = cli.download_report(uuid, as_element_tree=True)
                r.getroottree().write(filename)
                return True
        except exceptions.ElementNotFound:
            return False, "InvalidUUID"
        except exceptions.AuthenticationError:
            return False, "AuthError"
        except IOError:
            return False, "ConnectError"

    def parse_xml_to_csv(self, xml_filename, csv_filename, ips_only=False, hostname=None, min_severity=None,
                         max_severity=None, threat_level=None, matchfile=None):
        goxargs = ["./apps/OpenVAS/goxparse/goxparse.py", xml_filename]

        if ips_only:
            goxargs += ["-ips"]
        if hostname is not None:
            goxargs += ["-host", hostname]
        if min_severity is not None:
            goxargs += ["-cvssmin", str(min_severity)]
        if max_severity is not None:
            goxargs += ["-cvssmax", str(max_severity)]
        if threat_level is not None:
            goxargs += ["-threatlevel", threat_level]
        if matchfile is not None:
            goxargs += ["-matchfile", matchfile]

        with open(csv_filename, 'w') as f:
            subprocess.call(goxargs, stdout=f)

        return True, 'Success'

    def parse_csv_to_json(self, csv_filename, json_filename):
        with open(csv_filename, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            header = tuple(header)
            reader = csv.DictReader(f, header)
            r = []
            with open(json_filename, 'w') as f2:
                for row in reader:
                    r.append(row)
                json.dump(r, f2)
        return True, 'Success'


    # @event(pull_down)
    # def test_event_action(self, data):
    #     print("in app.py")
    #     print(data)
    #     return 'Success'
    #
    # def dummy_action(self):
    #     logger.debug("dummy")
    #     return True

    def valid_num(self, num):
        if num is not None:
            try:
                int(num)
                return True
            except ValueError:
                return False
        else:
            return True

    def valid_timetype(self, str):
        return str is None or str.lower() in ["second", "minute", "hour", "day", "week", "month", "year", "decade"]
