#!/usr/bin/env python
import os
import subprocess
from domain_controller import domain

__author__ = 'akurilin'


class Disk(object):
    valid_types = ("file", "block", "dir", "network", "volume")
    valid_devices = ("floppy", "disk", "cdrom", "lum")

    def __init__(self, type, device, source_file, target_dev=None,
                 driver_type=None):
        if type not in Disk.valid_types:
            raise domain.IllegalArgumentError(Disk.valid_types, type)
        self.type = type
        if device is not None and device not in Disk.valid_devices:
            print ("asd")
            raise domain.IllegalArgumentError(Disk.valid_devices, device)
        self.device = device
        self.source_file = source_file
        if device == "cdrom":
            self.readonly = True
        else:
            self.readonly = False
        if driver_type is None:
            if device == "cdrom":
                self.driver_type = "raw"
            elif device == "disk":
                self.driver_type = "qcow2"
        self.target_dev = target_dev

    @staticmethod
    def cdrom_init(source_file):
        return Disk("block", "cdrom", source_file)

    @staticmethod
    def disk_init(source_file):
        return Disk("file", "disk", source_file)

    def get_xml(self):
        child = [{"name": "driver",
                  "attrib": {"name": "qemu", "type": self.driver_type}},
                 {"name": "source", "attrib": {"file": self.source_file}}]
        if self.target_dev is not None:
            child.append(
                {"name": "target", "attrib": {"dev": self.target_dev}})
        return {"name": "disk",
                "attrib": {"type": self.type, "device": self.device},
                "child": child}

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

    def set_target_dev(self, dev):
        self.target_dev = dev

    def __str__(self):
        return "Disk: " + self.type + "; " + self.device
