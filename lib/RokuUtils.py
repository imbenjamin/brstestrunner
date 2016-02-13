#!/usr/bin/python

import requests
import xml.etree.ElementTree as ElementTree


class RokuUtils:
    device_ip = ""
    ecp_address = ""

    def __init__(self, ip):
        self.device_ip = ip
        self.ecp_address = "http://"+ip+":8060/"

    def keypress(self, key):
        requests.post(self.ecp_address+"keypress/"+key)

    def is_dev_installed(self) -> bool:
        result = False
        r = requests.get(self.ecp_address+"query/apps")
        xml_root = ElementTree.fromstring(r.text)
        for app in xml_root.iter("app"):
            if app.get("id") == "dev":
                result = True
                break
        return result

    def launch_dev_channel(self):
        requests.post(self.ecp_address+"launch/dev")
