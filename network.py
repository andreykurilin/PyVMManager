#!/usr/bin/env python

from virtinst.util import randomMAC
import domain

__author__ = 'akurilin'


class Network(object):
    valid_types = ("network", "bridge")

    def __init__(self, type, net_name, mac_address=None):
        if type not in Network.valid_types:
            raise domain.IllegalArgumentError(Network.valid_types, type)
        self.type = type
        self.net_name = net_name
        if mac_address is None:
            self.mac_address = randomMAC()
        else:
            self.mac_address = mac_address

    def get_xml(self):
        if self.type == "bridge":
            attr_name = "bridge"
        else:
            attr_name = "network"
        return {"name": "interface", "attrib": {"type": self.type}, "child": [
            {"name": "mac", "attrib": {"mac": self.mac_address}},
            {"name": "source", "attrib": {attr_name: self.net_name}}]}

    @staticmethod
    def init_default_network():
        return Network("network", "default")
