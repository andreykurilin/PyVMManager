#!/usr/bin/env python
import libvirt
import subprocess
import uuid as id
import os
import xml.etree.cElementTree as ET
from virtinst.util import randomMAC


__author__ = 'akurilin'
__uri__ = "qemu:///system"


class Domain(object):
    def __init__(self, name, memory, source_file, source_file_type=None, uuid=None, vcpu=1, os_type="hvm",
                 type_arch="x86_64", type_machine="pc-1.0", clock_offset="utc",
                 domain_type="kvm", emulator="/usr/bin/kvm", network_type="network", network="default",
                 mac_address=None):
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
        self.activity = {"on_poweroff": "destroy", "on_reboot": "restart", "on_crash": "restart"}
        self.domain_type = domain_type
        self.emulator = emulator
        self.disk = Disk(source_file, source_file_type)
        self.net = Network(network_type, network, mac_address)

    def __add_sub_element_to_xml__(self, parent, name, text=None, attrib=None):
        child = ET.SubElement(parent, name)
        if text is not None:
            child.text = text
        if attrib is not None:
            for key in attrib.keys():
                child.set(key, attrib[key])
        return child

    def get_xml(self):
        root = ET.Element("domain")
        root.set("type", self.domain_type)

        self.__add_sub_element_to_xml__(root, "name", text=self.name)
        self.__add_sub_element_to_xml__(root, "uuid", text=str(self.uuid))
        self.__add_sub_element_to_xml__(root, "memory", text=str(self.memory), attrib={"unit": "KiB"})
        self.__add_sub_element_to_xml__(root, "currentMemory", text=str(self.memory), attrib={"unit": "KiB"})
        self.__add_sub_element_to_xml__(root, "vcpu", text=str(self.vcpu))
        # Start configure OS
        os = self.__add_sub_element_to_xml__(root, "os")
        self.__add_sub_element_to_xml__(os, "type", text=self.os_type,
                                        attrib={"arch": self.type_arch, "machine": self.type_machine})
        self.__add_sub_element_to_xml__(os, "boot", attrib={"dev": "hd"})
        # End configure OS
        # Start configure features
        features = self.__add_sub_element_to_xml__(root, "features")
        self.__add_sub_element_to_xml__(features, "acpi")
        self.__add_sub_element_to_xml__(features, "apic")
        self.__add_sub_element_to_xml__(features, "pae")
        # End configure features
        self.__add_sub_element_to_xml__(root, "clock", attrib={"offset": self.clock_offset})
        self.__add_sub_element_to_xml__(root, "on_poweroff", text=self.activity["on_poweroff"])
        self.__add_sub_element_to_xml__(root, "on_reboot", text=self.activity["on_reboot"])
        self.__add_sub_element_to_xml__(root, "on_crash", text=self.activity["on_crash"])
        # Start configure Devices
        devices = self.__add_sub_element_to_xml__(root, "devices")
        self.__add_sub_element_to_xml__(devices, "emulator", self.emulator)
        # Start configure Disk
        disk = self.__add_sub_element_to_xml__(root, "disk", attrib={"type": "file", "device": "disk"})
        self.__add_sub_element_to_xml__(disk, "driver",
                                        attrib={"name": self.disk.driver_name, "type": self.disk.source_file_type})
        self.__add_sub_element_to_xml__(disk, "source", attrib={"file": self.disk.source_file})
        self.__add_sub_element_to_xml__(disk, "target",
                                        attrib={"dev": self.disk.target["dev"], "bus": self.disk.source_file_type})
        # End configure Disk
        # Start configure Network
        interface = self.__add_sub_element_to_xml__(devices, "interface", attrib={"type": self.net.type})
        self.__add_sub_element_to_xml__(interface, "mac", attrib={"address": self.net.mac_address})
        self.__add_sub_element_to_xml__(interface, "source", attrib={"network": self.net.network})
        # End configure Network
        # Start configure extra settings
        console = self.__add_sub_element_to_xml__(devices, "console", attrib={"type": "pty"})
        self.__add_sub_element_to_xml__(console, "target", attrib={"type": "serial", "port": "0"})
        self.__add_sub_element_to_xml__(devices, "input", attrib={"type": "mouse", "bus": "ps2"})
        self.__add_sub_element_to_xml__(devices, "graphics", attrib={"type": "vnc", "port": "-1", "autoport": "yes"})
        video = self.__add_sub_element_to_xml__(devices, "video")
        self.__add_sub_element_to_xml__(video, "model", attrib={"type": "cirrus", "vram": "9216", "heads": "1"})
        # End configure Devices

        return ET.tostring(root)

    def config_from_list(self, conf_list):
        #name, memory, source_file, source_file_type=None, uuid=None, vcpu=1, os_type="hvm",
        #         type_arch="x86_64", type_machine="pc-1.0", clock_offset="utc",
        #         domain_type="kvm", emulator="/usr/bin/kvm", network_type="network", network="default",
        #         mac_address=None
        for each in conf_list:
            if each[0:3] == "name":
                self.name = each[5:]
            elif each[0:5] == "img":
                self.memory = each[7:]
            elif each[0:2] == "img":
                self.disk = Disk(each[4:], self.disk.source_file_type)
            elif each[0:7] == "img_type":
                self.disk = Disk(self.disk.source_file, each[9:])
            elif each[0:3] == "uuid":
                self.uuid = each[5:]
            elif each[0:3] == "vcpu":
                self.disk = Disk(each[4:], self.disk.source_file_type)
            elif each[0:7] == "os_type":
                self.disk = Disk(self.disk.source_file, each[9:])

    # Create VM
    def create(self, uri=__uri__):
        connection = libvirt.open(uri)
        connection.defineXML(self.get_xml())
        connection.close()


class Disk(object):
    @staticmethod
    def get_file_type(source_file):
        if os.path.isfile(source_file):
            cmd = "qemu-img info " + source_file
            qemu_img = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            qemu_img_result = qemu_img.communicate()
            lst = qemu_img_result[0].split()
            for i in range(0, lst.__len__() - 1):
                if lst[i] == "format:":
                    return lst[i + 1]
            return None

    def __init__(self, source_file, source_file_type=None, driver_name="qemu"):
        self.driver_name = driver_name
        self.target = {"dev": "hda", "bus": "ide"}
        self.address = {"type": "drive", "controller": "0", "bus": "0", "unit": "0"}
        self.source_file = source_file
        if source_file_type is None:
            self.source_file_type = Disk.get_file_type(source_file)
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