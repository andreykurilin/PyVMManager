#!/usr/bin/env python
import libvirt
from domain_controller.disk import Disk
from domain_controller.domain import Domain
from domain_controller.network import Network
from xml_utils import xml_to_string
from settings import conf

__author__ = 'akurilin'


class Controller(object):
    """ Represent management system(create/delete/power on/ power off/reboot)
    VM using libvirt python api.

    Keyword arguments:
    uri -- hypervisor connection URI
    error_flag -- the key that determines whether the exceptions are raised.
        (default False)
    """
    def __init__(self, uri, error_flag=False):
        self.uri = uri
        self.error_flag = error_flag
        self.connection = None
        self.connection = self.get_connection()
        Domain.DEFAULT_VALUES = conf.Domain
        Disk.valid_types = conf.Disk["valid_types"]
        Disk.valid_devices = conf.Disk["valid_devices"]
        Network.valid_types = conf.Network["valid_types"]

    def get_connection(self):
        if self.connection is None or not self.connection.isAlive():
            try:
                self.connection = libvirt.open(self.uri)
                return self.connection
            except libvirt.libvirtError:
                error_flag = ConnectionError(self.uri)
                print error_flag
                if self.error_flag:
                    raise error_flag
        return self.connection

    def get_domains(self):
        dict = {}
        for id in self.get_connection().listDomainsID():
            domain = self.get_connection().lookupByID(id)
            dict[domain.name()] = {"status": "running", "id": id,
                                   "name": domain.name()}
        for defined_domain in self.get_connection().listDefinedDomains():
            dict[defined_domain] = {"status": "shutdown", "id": "-",
                                    "name": defined_domain}
        return dict

    def start(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            if domains[str(args["name"])]["status"] == "running":
                print ("Virtual machine \"{0}"
                       "\" already started.".format(args["name"]))
            else:
                print ("Starting \"" + args["name"] + "\"...")
                self.get_connection().lookupByName(args["name"]).create()
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def stop(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            if domains[args["name"]]["status"] == "shutdown":
                error = NotRunningError(args["name"])
                print error
                if self.error_flag:
                    raise error
            else:
                print ("Try to stop \"{0}\"...".format(args["name"]))
                self.get_connection().lookupByName(args["name"]).shutdown()
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def forced_stop(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            if domains[args["name"]]["status"] == "shutdown":
                print ("Virtual machine \"{0}"
                       "\" is not running.".format(args["name"]))
            else:
                print ("Forced stop \"{0}\"...".format(args["name"]))
                self.get_connection().lookupByName(args["name"]).destroy()
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def reboot(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            if domains[args["name"]]["status"] == "shutdown":
                print ("Virtual machine \"{0}"
                       "\" is not running.".format(args["name"]))
            else:
                print ("Send reboot signal to \"" + args["name"] + "\"...")
                self.get_connection().lookupByName(args["name"]).destroy()
                self.get_connection().lookupByName(args["name"]).create()
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def list(self, args):
        vert_delimiter = "\t| "
        hor_delimiter = "---------------------------------------" \
                        "----------------------------------------"
        print hor_delimiter
        print "id" + vert_delimiter + "Status" + vert_delimiter + "Domain"
        print hor_delimiter

        domains = self.get_domains()
        for name in domains.keys():
            if domains[name]["status"] == "shutdown" and \
                args["select"] == "all" or \
                    domains[name]["status"] != "shutdown":
                print "{1}{0}{2}{0}{3}".format(vert_delimiter,
                                               domains[name]["id"],
                                               domains[name]["status"],
                                               domains[name]["name"])

    def create(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            error = AlreadyCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error
        else:
            domain = Domain(args["name"], args["memory"], args["uuid"],
                            args["vcpu"],args["os_type"], args["type_arch"],
                            args["type_machine"], args["clock_offset"],
                            args["domain_type"], args["emulator"])
            if "disks" in args and args["disks"] is not None:
                for disk in args["disks"]:
                    domain.add_disk(disk, "disk")
            if "cdroms" in args and args["cdroms"] is not None:
                for cdrom in args["cdroms"]:
                    domain.add_disk(cdrom, "cdrom")
            if "nets" in args and args["nets"] is not None:
                for net in args["nets"]:
                    domain.add_network(net_name=net)
            if "bridges" in args and args["bridges"] is not None:
                for br in args["bridges"]:
                    domain.add_network(net_type="bridge", net_name=br)

            print ("Try to create \"" + domain.name + "\"")
            self.get_connection().defineXML(xml_to_string(domain.get_xml()))

    def remove(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            if domains[args["name"]]["status"] != "shutdown":
                print ("Forced stop \"" + args["name"] + "\"...")
                self.get_connection().lookupByName(args["name"]).destroy()
            print ("Delete \"" + args["name"] + "\".")
            self.get_connection().lookupByName(args["name"]).undefine()
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def info(self, args):
        domains = self.get_domains()
        if args["name"] in domains.keys():
            infos = self.get_connection().lookupByName(args["name"]).info()
            domain_info = {"name": args["name"],
                           "state": infos[0],
                           "memory": infos[1],
                           "vcpu": infos[3],
                           "cpu_time": infos[2]}
            return domain_info
        else:
            error = NotCreatedVMError(args["name"])
            print error
            if self.error_flag:
                raise error

    def show_info(self, args):
        domain_info = self.info(args)
        print 'Name =  %s' % domain_info["name"]
        print 'State = %d' % domain_info["state"]
        print 'Max Memory = %d' % domain_info["memory"]
        print 'Number of virt CPUs = %d' % domain_info["vcpu"]
        print 'CPU Time (in ns) = %d' % domain_info["cpu_time"]


class ConnectionError(Exception):
    def __init__(self, uri):
        self.uri = uri

    def __str__(self):
        return "Can't connect to \"{0}\"".format(self.uri)


class VMError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        raise NotImplementedError()


class AlreadyCreatedVMError(VMError):
    def __str__(self):
        return "Virtual machine \"{0}\" already created.".format(self.name)


class NotCreatedVMError(VMError):
    def __str__(self):
        return "Virtual machine \"{0}\" is not created yet.".format(self.name)


class NotRunningError(VMError):
    def __str__(self):
        return "Virtual machine \"{0}\" is not running.".format(self.name)