#!/usr/bin/env python

__author__ = 'akurilin'


class Disk(object):
    valid_types = ("file", "block", "dir", "network", "volume")
    valid_devices = ("floppy", "disk", "cdrom", "lum")

    def __init__(self, type, device, source_file, target_dev=None,
                 driver_type=None):
        if type not in Disk.valid_types:
            raise Disk.IllegalArgumentError(Disk.valid_types, type)
        self.type = type
        if device is not None and type not in Disk.valid_devices:
            raise Disk.IllegalArgumentError(Disk.valid_devices, device)
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
        {}

    def set_target_dev(self, dev):
        self.target_dev = dev

    def __str__(self):
        return "Disk: " + self.type + "; " + self.device

    class IllegalArgumentError(ValueError):
        def __init__(self, valid_args, invalid_arg):
            self.valid_args = valid_args
            self.invalid_arg = invalid_arg

        def __str__(self):
            return " Illegal argument \"" \
                   + self.invalid_arg + "\". Allowed arguments: " \
                   + str(self.valid_args).replace("(", "").replace(")",
                                                                   "") + "."