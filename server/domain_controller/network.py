#!/usr/bin/env python

from virtinst.util import randomMAC
from server.domain_controller.disk import IllegalArgumentError

__author__ = 'akurilin'


class Network():
    """ Represent network interface.

    Keyword arguments:
    type -- type of disk
        (tuple of allowed types assigned to "valid_types" variable)
    device -- type of disk device
        (tuple of allowed devices assigned to "valid_devices" variable)
    source_file -- path to source file of disk image
    target_dev -- target where disk will mounted(default None)
    driver_type -- type of disk driver
    """
    valid_types = ()

    def __init__(self, type, net_name, mac_address=None):
        if type not in Network.valid_types:
            raise IllegalArgumentError(Network.valid_types, type)
        self.type = type
        self.net_name = net_name
        if mac_address is None:
            self.mac_address = randomMAC()
        else:
            self.mac_address = mac_address

    def get_domain_xml(self):
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
