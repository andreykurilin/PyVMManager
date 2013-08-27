#!/usr/bin/env python
import libvirt
from domain_controller.domain import Domain
from xml_utils import xml_to_string

__author__ = 'akurilin'


class Controller(object):
    def __init__(self, uri, error_flag=False, Namespace=True):
        self.uri = uri
        self.error_flag = error_flag
        self.connection = None
        self.connection = self.get_connection()
        self.namespace_flag = Namespace

    @staticmethod
    def namespace(func):
        def decorated(self, args):
            if self.namespace_flag:
                args = vars(args)
            return func(self, args)
        return decorated

    def get_connection(self):
        if self.connection is not None and self.connection.isAlive():
            return self.connection
        else:
            try:
                self.connection = libvirt.open(self.uri)
            except libvirt.libvirtError:
                error_flag = ConnectionError(self.uri)
                print error_flag
                if self.error_flag:
                    raise error_flag

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

    @namespace
    def start_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            if domains[str(args["vm_name"])]["status"] == "running":
                print ("Virtual machine \"{0}"
                       "\" already started.".format(args.vm_name))
            else:
                print ("Starting \"" + args["vm_name"] + "\"...")
                self.get_connection().lookupByName(args["vm_name"]).create()
        else:
            error = NotCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error

    @namespace
    def stop_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            if domains[args["vm_name"]]["status"] == "shutdown":
                print ("Virtual machine \"{0}"
                       "\" is not running.".format(args["vm_name"]))
            else:
                print ("Try to stop \"{0}\"...".format(args["vm_name"]))
                self.get_connection().lookupByName(args["vm_name"]).shutdown()
        else:
            error = NotCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error

    @namespace
    def forced_stop_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            if domains[args["vm_name"]]["status"] == "shutdown":
                print ("Virtual machine \"{0}"
                       "\" is not running.".format(args["vm_name"]))
            else:
                print ("Forced stop \"{0}\"...".format(args["vm_name"]))
                self.get_connection().lookupByName(args["vm_name"]).destroy()
        else:
            error = NotCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error

    @namespace
    def reboot_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            if domains[args["vm_name"]]["status"] == "shutdown":
                print ("Virtual machine \"{0}"
                       "\" is not running.".format(args.vm_name))
            else:
                print ("Send reboot signal to \"" + args["vm_name"] + "\"...")
                self.get_connection().lookupByName(args["vm_name"]).reboot()
        else:
            error = NotCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error

    @namespace
    def show_vm_list(self, args):
        vert_delimiter = "\t| "
        hor_delimiter = "---------------------------------------" \
                        "----------------------------------------"
        print hor_delimiter
        print "id" + vert_delimiter + "Status" + vert_delimiter + "Domain"
        print hor_delimiter

        domains = self.get_domains()
        for name in domains.keys():
            if domains[name]["status"] == "shutdown" and \
                args["list_select"] == "all" or \
                    domains[name]["status"] != "shutdown":
                print "{1}{0}{2}{0}{3}".format(vert_delimiter,
                                               domains[name]["id"],
                                               domains[name]["status"],
                                               domains[name]["name"])

    @namespace
    def create_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            error = AlreadyCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error
        else:
            domain = Domain(args["vm_name"], args["memory"], args["uuid"],
                            args["vcpu"],args["os_type"], args["type_arch"],
                            args["type_machine"], args["clock_offset"],
                            args["domain_type"], args["emulator"])
            if args["disks"] is not None:
                for disk in args["disks"]:
                    domain.add_disk(disk, "disk")
            if args["cdroms"] is not None:
                for cdrom in args["cdroms"]:
                    domain.add_disk(cdrom, "cdrom")
            if args["nets"] is not None:
                for net in args["nets"]:
                    domain.add_network(net_name=net)
            if args["bridges"] is not None:
                for br in args["bridges"]:
                    domain.add_network(net_type="bridge", net_name=br)

            print ("Try to create \"" + domain.name + "\"")
            self.get_connection().defineXML(xml_to_string(domain.get_xml()))

    @namespace
    def remove_vm(self, args):
        domains = self.get_domains()
        if args["vm_name"] in domains.keys():
            if domains[args["vm_name"]]["status"] != "shutdown":
                print ("Forced stop \"" + args["vm_name"] + "\"...")
                self.get_connection().lookupByName(args["vm_name"]).destroy()
            print ("Delete \"" + args["vm_name"] + "\".")
            self.get_connection().lookupByName(args["vm_name"]).undefine()
        else:
            error = NotCreatedVMError(args["vm_name"])
            print error
            if self.error_flag:
                raise error


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