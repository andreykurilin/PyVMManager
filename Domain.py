#!/usr/bin/env python
import libvirt
import subprocess
import uuid as id
import os
import xml.etree.cElementTree as ET
from virtinst.util import randomMAC
import Disk
from xml_utils import *


__author__ = 'akurilin'
__uri__ = "qemu:///system"


class Domain(object):
    def __init__(self, name, memory, uuid=None, vcpu=1, os_type="hvm",
                 type_arch="x86_64", type_machine="pc-1.0", clock_offset="utc",
                 domain_type="kvm", emulator="/usr/bin/kvm",
                 network_type="network", network="default", mac_address=None):
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
        self.net = Network(network_type, network, mac_address)
        self.disks = []

    def add_disk(self, file, device):
        if device == "cdrom":
            self.disks.append(Disk.cdrom_init(file))
        elif device == "disk":
            self.disks.append(Disk.disk_init(file))

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
        for i in range(0, self.disks.__len__()):
            self.disks[i].set_target_dev("hd" + str(chr(97 + i)))
            devices["child"].append(self.disks[i].get_xml())

        return {}

        # Start configure Disk
        #disk = self._add_sub_element_to_xml(root, "disk",
        #                                    attrib={"type": "file",
        #                                            "device": "disk"})
        #self._add_sub_element_to_xml(disk, "driver",
        #                             attrib={"name": self.disk.driver_name,
        #                                     "type": self.disk.source_file_type})
        #self._add_sub_element_to_xml(disk, "source",
        #                             attrib={"file": self.disk.source_file})
        #self._add_sub_element_to_xml(disk, "target",
        #                             attrib={"dev": self.disk.target["dev"],
        #                                     "bus": self.disk.source_file_type})
        # End configure Disk
        # Start configure Network
        #interface = self._add_sub_element_to_xml(devices, "interface", attrib={
        #    "type": self.net.type})
        #self._add_sub_element_to_xml(interface, "mac",
        #                             attrib={"address": self.net.mac_address})
        #self._add_sub_element_to_xml(interface, "source",
        #                             attrib={"network": self.net.network})
        # End configure Network
        # Start configure extra settings
        #console = self._add_sub_element_to_xml(devices, "console",
        #                                       attrib={"type": "pty"})
        #self._add_sub_element_to_xml(console, "target",
        #                             attrib={"type": "serial", "port": "0"})
        #self._add_sub_element_to_xml(devices, "input",
        #                             attrib={"type": "mouse", "bus": "ps2"})
        #self._add_sub_element_to_xml(devices, "graphics",
        #                             attrib={"type": "vnc", "port": "-1",
        #                                     "autoport": "yes"})
        #video = self._add_sub_element_to_xml(devices, "video")
        #self._add_sub_element_to_xml(video, "model",
        #                             attrib={"type": "cirrus", "vram": "9216",
        #                                     "heads": "1"})
        # End configure Devices

    def get_xml(self):
        return {"name": "domain",
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
                ]}

    # Create VM
    def create(self, uri=__uri__):
        connection = libvirt.open(uri)
        connection.defineXML(xml_to_string(self.get_xml()))
        connection.close()


class Disk_img(object):
    @staticmethod
    def get_file_type(source_file):
        if os.path.isfile(source_file):
            cmd = "qemu-img info " + source_file
            qemu_img = subprocess.Popen(cmd, shell=True,
                                        stdout=subprocess.PIPE)
            qemu_img_result = qemu_img.communicate()
            lst = qemu_img_result[0].split()
            for i in range(0, lst.__len__() - 1):
                if lst[i] == "format:":
                    return lst[i + 1]
            return None

    def __init__(self, source_file, source_file_type=None, driver_name="qemu"):
        self.driver_name = driver_name
        self.target = {"dev": "hda", "bus": "ide"}
        self.address = {"type": "drive", "controller": "0", "bus": "0",
                        "unit": "0"}
        self.source_file = source_file
        if source_file_type is None:
            self.source_file_type = Disk_img.get_file_type(source_file)
        else:
            self.source_file_type = source_file_type


class Network(object):
    def __init__(self, type="network", network="default", mac_address=None):
        self.type = type
        self.network = network
        if mac_address is None:
            self.mac_address = randomMAC()
        else:
            self.mac_address = mac_address