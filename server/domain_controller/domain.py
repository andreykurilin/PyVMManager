#!/usr/bin/env python

import libvirt
import uuid as id
import xml.etree.cElementTree as ET
from sqlalchemy import *
from sqlalchemy.orm import relationship
from server.domain_controller.disk import *
from network import Network
from server.db.tables import Base
from server.utils.settings import conf
from server.utils.xml_shaper import *


__author__ = 'akurilin'
__uri__ = "qemu:///system"


class Domain(Base):
    _DEFAULT_VALUES = {"state": conf.Domain["state"],
                      "vcpu": conf.Domain["vcpu"],
                      "os_type": conf.Domain["os_type"],
                      "type_arch": conf.Domain["type_arch"],
                      "type_machine": conf.Domain["type_machine"],
                      "clock_offset": conf.Domain["clock_offset"],
                      "domain_type": conf.Domain["domain_type"],
                      "emulator": conf.Domain["emulator"]}
    __tablename__ = 'domains'

    uuid_str = Column(String(100), primary_key=True)
    name = Column(String(100))
    memory = Column(String(100))
    host_id = Column(Integer, ForeignKey('hosts.id'))
    state_id = Column(Integer, ForeignKey('states.id'))
    mac = Column(String(300), primary_key=True)
    actions = relationship("Action", backref="domain")

    def __init__(self, name, memory, host_id=1, mac_address="",
                 state=_DEFAULT_VALUES["state"],
                 uuid_str=None,
                 vcpu=_DEFAULT_VALUES["vcpu"],
                 os_type=_DEFAULT_VALUES["os_type"],
                 type_arch=_DEFAULT_VALUES["type_arch"],
                 type_machine=_DEFAULT_VALUES["type_machine"],
                 clock_offset=_DEFAULT_VALUES["clock_offset"],
                 domain_type=_DEFAULT_VALUES["domain_type"],
                 emulator=_DEFAULT_VALUES["emulator"]):
        self.name = name
        self.memory = memory
        if uuid_str is None:
            self.uuid_str = str(id.uuid1())
        else:
            self.uuid_str = uuid_str
        self.vcpu = vcpu
        self.os_type = os_type
        self.type_arch = type_arch
        self.type_machine = type_machine
        self.clock_offset = clock_offset
        self.activity = {"on_poweroff": "destroy", "on_reboot": "restart",
                         "on_crash": "restart"}
        self.domain_type = domain_type
        self.emulator = emulator
        self.disks = []
        self.nets = []
        self.state_id = state
        self.host_id = host_id
        self.mac = mac_address

    def add_disk(self, source_file, device):
        if device == "cdrom":
            self.disks.append(Disk.cdrom_init(source_file))
        elif device == "disk":
            self.disks.append(Disk.disk_init(source_file))

    def add_network(self, net_type="network", net_name="default",
                    mac_address=None):
        net = Network(net_type, net_name, mac_address)
        self.mac_address = net.mac_address
        self.nets.append(net)

    def _add_sub_element_to_xml(self, parent, name, text=None, attrib=None):
        child = ET.SubElement(parent, name)
        if text is not None:
            child.text = text
        if attrib is not None:
            for key in attrib.keys():
                child.set(key, attrib[key])
        return child

    def get_devices(self):
        devices = {"name": "devices", "child": [
            {"name": "emulator", "text": self.emulator},
        ]}
        if self.disks.__len__() != 0:
            for i in range(0, self.disks.__len__()):
                self.disks[i].set_target_dev("hd" + str(chr(97 + i)))
                devices["child"].append(self.disks[i].get_xml())
        if self.nets.__len__() != 0:
            net = Network.init_default_network()
            self.mac_address += net.mac_address + ";"
            self.nets.append(net)
        for net in self.nets:
            devices["child"].append(net.get_domain_xml())
        devices["child"].append(
            {"name": "console",
             "attrib": {"type": "pty"},
             "child": [{"name": "serial",
                        "attrib": {"type": "serial", "port": "0"}}]})
        devices["child"].append(
            {"name": "input",
             "attrib": {"type": "mouse", "bus": "ps2"}})
        devices["child"].append(
            {"name": "graphics",
             "attrib": {"type": "vnc", "port": "-1", "autoport": "yes"},
             "child": [{"name": "model",
                        "attrib": {"type": "cirrus",
                                   "vram": "9216",
                                   "heads": "1"}}]})
        return devices

    def get_xml(self):
        return add_elements(
            {"name": "domain",
                "attrib": {"type": self.domain_type},
                "child": [
                    {"name": "name", "text": self.name},
                    {"name": "uuid", "text": str(self.uuid_str)},
                    {"name": "memory", "text": str(self.memory),
                     "attrib": {"unit": "KiB"}},
                    {"name": "currentMemory", "text": str(self.memory),
                     "attrib": {"unit": "KiB"}},
                    {"name": "vcpu", "text": str(self.vcpu)},
                    {"name": "os",
                     "child": [
                         {"name": "type", "text": self.os_type,
                          "attrib": {"arch": self.type_arch,
                                     "machine": self.type_machine}},
                         {"name": "boot", "attrib": {"dev": "hd"}}
                     ]},
                    {"name": "features",
                     "child": [
                         {"name": "acpi"},
                         {"name": "apic"},
                         {"name": "pae"}
                     ]},
                    {"name": "clock", "attrib": {"offset": self.clock_offset}},
                    {"name": "on_poweroff", "text": self.activity["on_poweroff"]},
                    {"name": "on_reboot", "text": self.activity["on_reboot"]},
                    {"name": "on_crash", "text": self.activity["on_crash"]},
                    self.get_devices()
                ]})

    # Create VM
    def create(self, uri=__uri__):
        connection = libvirt.open(uri)
        print xml_to_string(self.get_xml())
        connection.defineXML(xml_to_string(self.get_xml()))
        connection.close()

    def __repr__(self):
        return "<Domain('%s', '%s', '%s', '%s', '%s', '%s')>" % \
               (self.name, self.memory, self.uuid_str, self.state, self.host_id,
                self.mac_address)
