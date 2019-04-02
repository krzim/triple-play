
from proxmoxer import ProxmoxAPI
import socket
import asyncio
import time
import logging

from app_sdk.app_base import AppBase
logger = logging.getLogger("apps")

class Proxmox(AppBase):
    __version__ = "v1.0"
    def __init__(self, redis=None, logger=None):
        super().__init__(redis, logger)

    def get_proxmox(self, username, password, host):
        return ProxmoxAPI(host, user=username,
                                  password=password, verify_ssl=False)

    def get_all_nodes(self, username, password, host):
        proxmox = get_proxmox(username, password, host)
        return proxmox.nodes.get()

    def get_all_vms(self, username, password, host):
        proxmox = get_proxmox(username, password, host)
        nodes_vms = []
        for node in proxmox.nodes.get():
            node['vms'] = []
            for vm in proxmox.nodes(node['node']).openvz.get():
                node['vms'].append(vm)
            nodes_vms.append(node)


    def get_all_vms_for_node(self, node_name, username, password, host):
      proxmox = get_proxmox(username, password, host)
      for node in proxmox.nodes.get():

