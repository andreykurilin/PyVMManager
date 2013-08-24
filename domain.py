#!/usr/bin/env python

import libvirt
import uuid as id
import xml.etree.cElementTree as ET
from disk import disk
from network import Network
from xml_utils import *


__author__ = 'akurilin'
__uri__ = "qemu:///system"


class Domain(object):
    def __init__(self, name, memory, uuid=None, vcpu=1, os_type="hvm",
                 type_arch="x86_64", type_machine="pc-1.0", clock_offset="utc",
                 domain_type="kvm", emulator="/usr/bin/kvm"):
        self.name = name
        self.memory = memory
        if uuid is None:
            self.uuid = str(id.uuid1())
        else:
            self.uuid = uuid
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

    def add_disk(self, file, device):
        if device == "cdrom":
            self.disks.append(disk.cdrom_init(file))
        elif device == "disk":
            self.disks.append(disk.disk_init(file))

    def add_network(self, type="network", net_name="default",
                    mac_address=None):
        self.nets.append(Network(type, net_name, mac_address))

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
            for net in self.nets:
                devices["child"].append(net.get_xml())
        devices["child"].append(
            {"name": "console", "attrib": {"type": "pty"}, "child": [
                {"name": "serial",
                 "attrib": {"type": "serial", "port": "0"}}]})
        devices["child"].append(
            {"name": "input", "attrib": {"type": "mouse", "bus": "ps2"}})
        devices["child"].append({"name": "graphics",
                                 "attrib": {"type": "vnc", "port": "-1",
                                            "autoport": "yes"}, "child": [
            {"name": "model",
             "attrib": {"type": "cirrus", "vram": "9216", "heads": "1"}}]})

        return devices

    def get_xml(self):
        return add_elements({"name": "domain",
                "attrib": {"type": self.domain_type},
                "child": [
                    {"name": "name", "text": self.name},
                    {"name": "uuid", "text": str(self.uuid)},
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
                    {"name": "on_poweroff",
                     "text": self.activity["on_poweroff"]},
                    {"name": "on_reboot", "text": self.activity["on_reboot"]},
                    {"name": "on_crash", "text": self.activity["on_crash"]},
                    self.get_devices()
                ]})

    # Create VM
    def create(self, uri=__uri__):
        connection = libvirt.open(uri)
        connection.defineXML(xml_to_string(self.get_xml()))
        connection.close()


class IllegalArgumentError(ValueError):
    def __init__(self, valid_args, invalid_arg):
        self.valid_args = valid_args
        self.invalid_arg = invalid_arg

    def __str__(self):
        return " Illegal argument \"" \
               + self.invalid_arg + "\". Allowed arguments: " \
               + str(self.valid_args).replace("(", "").replace(")", "") \
               + "."
