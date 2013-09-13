#!/usr/bin/env python

import os
import signal
from server.utils.settings import conf

__author__ = 'akurilin'


class Controller(object):
    def __init__(self):
        self.address = []
        self.config = {"file": conf.DNSMasq["config"],
                       "leases": conf.DNSMasq["leases"],
                       "interfaces": conf.DNSMasq["interfaces"].split(","),
                       "hosts": conf.DNSMasq["hosts"],
                       "pid": conf.DNSMasq["pid"]}

    def add_address(self, ip_address, mac_address=None):
        if mac_address == "-":
            mac_address = None
        for address in self.address:
            if address["ip"] == ip_address:
                address["mac"] = mac_address
                return
        self.address.append({"ip": ip_address, "mac": mac_address})

    def read(self):
        file_in = open(self.config["file"])
        for line in file_in.readlines():
            text = line.replace("\n", "").split("=")
            if text[0] == "dhcp-range":
                self.add_address(text[1].split(",")[0])
        file_in.close()
        file_in = open(self.config["hosts"])
        for line in file_in.readlines():
            host = line.split(",")
            self.add_address(host[1], host[0])
        file_in.close()

    def write(self):
        file_out = open(self.config["file"], 'w')
        host_out = open(self.config["hosts"], 'w')
        file_out.writelines(["interface={0}\n".format(line)
                             for line in self.config["interfaces"]])
        file_out.write("dhcp-leasefile={0}\n".format(self.config["leases"]))
        file_out.write("dhcp-hostsfile={0}\n".format(self.config["hosts"]))
        print self.address
        for address in self.address:
            if address["mac"] is not None:
                host_out.write("dhcp-host={0},{1}\n".format(
                    address["mac"], address["ip"]))
            else:
                file_out.write("dhcp-range={0},{0},24h\n".format(
                    address["ip"]))
        file_out.close()
        host_out.close()

    def parse_leases(self):
        file_in = open(self.config["leases"])
        for line in file_in.readlines():
            line_content = line.split(" ")
            if line_content.__len__() >=2:
                self.add_address(line_content[2], line_content[1])
        file_in.close()

    def clear_leases(self):
        file_out = open(self.config["leases"], "w")
        file_out.write("")
        file_out.close()

    def sighup(self):
        if os.path.isfile(self.config["pid"]):
            pid = int(open(self.config["pid"]).readline())
            os.kill(pid, signal.SIGHUP)