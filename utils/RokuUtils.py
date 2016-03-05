#!/usr/bin/env python

import xml.etree.ElementTree as ElementTree
import urllib2


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
        try:
            urllib2.urlopen(self.ecp_address + "keypress/" + key, "").read()
            return True
        except urllib2.HTTPError:
            return False

    def is_dev_installed(self):
        """Checks if there is a 'dev' channel installed on the Roku device
        :return: Boolean result
        """
        result = False
        try:
            r = urllib2.urlopen(self.ecp_address + "query/apps").read()
            xml_root = ElementTree.fromstring(r)
            for app in xml_root.getiterator("app"):
                if app.get("id") == "dev":
                    result = True
                    break
        except urllib2.HTTPError:
            result = False
        return result

    def launch_dev_channel(self):
        """Commands that the 'dev' channel is launched
        """
        try:
            urllib2.urlopen(self.ecp_address + "launch/dev", "").read()
            return True
        except urllib2.HTTPError:
            return False
