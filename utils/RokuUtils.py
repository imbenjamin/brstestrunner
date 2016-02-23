#!/usr/bin/python

import xml.etree.ElementTree as ElementTree

from utils import requests


class RokuUtils:
    """Utilites for Roku devices
    :param ip: The IP address of the Roku device to use
    """
    device_ip = ""
    ecp_address = ""

    def __init__(self, ip):
        self.device_ip = ip
        self.ecp_address = "http://"+ip+":8060/"

    def keypress(self, key):
        """Commands a key press
        :param key: A valid key name
        """
        requests.post(self.ecp_address + "keypress/" + key)

    def is_dev_installed(self):
        """Checks if there is a 'dev' channel installed on the Roku device
        :return: Boolean result
        """
        result = False
        r = requests.get(self.ecp_address + "query/apps")
        xml_root = ElementTree.fromstring(r.text)
        for app in xml_root.getiterator("app"):
            if app.get("id") == "dev":
                result = True
                break
        return result

    def launch_dev_channel(self):
        """Commands that the 'dev' channel is launched
        """
        requests.post(self.ecp_address + "launch/dev")
