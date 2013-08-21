#!/usr/bin/env python
import subprocess

__author__ = 'akurilin'
import uuid as id
import os
from virtinst.util import randomMAC
from virtinst.util import randomUUID


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

    def get_xml(self):
        import xml.etree.cElementTree as ET

        root = ET.Element("domain")
        root.set("type", self.domain_type)

        name = ET.SubElement(root, "name")
        name.text = self.name

        uuid = ET.SubElement(root, "uuid")
        uuid.text = str(self.uuid)

        memory = ET.SubElement(root, "memory")
        memory.set("unit", "KiB")
        memory.text = str(self.memory)

        cur_memory = ET.SubElement(root, "currentMemory")
        cur_memory.set("unit", "KiB")
        cur_memory.text = str(self.memory)

        vcpu = ET.SubElement(root, "vcpu")
        vcpu.text = str(self.vcpu)

        # Start configure OS
        os = ET.SubElement(root, "os")
        os_type = ET.SubElement(os, "type")
        os_type.set("arch", self.type_arch)
        os_type.set("machine", self.type_machine)
        os_type.text = self.os_type

        boot = ET.SubElement(os, "boot")
        boot.set("dev", "hd")
        # End configure OS

        features = ET.SubElement(root, "features")
        ET.SubElement(features, "acpi")
        ET.SubElement(features, "apic")
        ET.SubElement(features, "pae")

        clock = ET.SubElement(root, "clock")
        clock.set("offset", self.clock_offset)

        on_poweroff = ET.SubElement(root, "on_poweroff")
        on_poweroff.text = self.activity["on_poweroff"]

        on_reboot = ET.SubElement(root, "on_reboot")
        on_reboot.text = self.activity["on_reboot"]

        on_crash = ET.SubElement(root, "on_crash")
        on_crash.text = self.activity["on_crash"]

        devices = ET.SubElement(root, "devices")

        emulator = ET.SubElement(devices, "emulator")
        emulator.text = self.emulator

        # Start configure Disk
        disk = ET.SubElement(devices, "disk")
        disk.set("type", "file")
        disk.set("device", "disk")

        driver = ET.SubElement(disk, "driver")
        driver.set("name", self.disk.driver_name)
        driver.set("type", self.disk.source_file_type)

        source_img = ET.SubElement(disk, "source")
        source_img.set("file", self.disk.source_file)

        target = ET.SubElement(disk, "target")
        target.set("dev", self.disk.target["dev"])
        target.set("bus", self.disk.target["bus"])
        # End configure Disk

        # Start configure Network
        interface = ET.SubElement(devices, "interface")
        interface.set("type", self.net.type)

        mac = ET.SubElement(interface, "mac")
        mac.set("address", self.net.mac_address)

        source = ET.SubElement(interface, "source")
        source.set("network", self.net.network)
        # End configure Network

        console = ET.SubElement(devices, "console")
        console.set("type", "pty")

        target = ET.SubElement(console, "target")
        target.set("type", "serial")
        target.set("port", "0")

        input = ET.SubElement(devices, "input")
        input.set("type", "mouse")
        input.set("bus", "ps2")

        graphics = ET.SubElement(devices, "graphics")
        graphics.set("type", "vnc")
        graphics.set("port", "-1")
        graphics.set("autoport", "yes")

        video = ET.SubElement(devices, "video")
        model = ET.SubElement(video, "model")
        model.set("type", "cirrus")
        model.set("vram", "9216")
        model.set("heads", "1")

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