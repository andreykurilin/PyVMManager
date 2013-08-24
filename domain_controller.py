#!/usr/bin/env python
import libvirt
from domain import Domain
from xml_utils import xml_to_string

__author__ = 'akurilin'


def libvirt_connection(func):
    def decorated(args):
        try:
            connection = libvirt.open(args.uri)
            func(args, connection)
        except libvirt.libvirtError:
            print "Can't connect to URI"
        finally:
            if "connection" in locals() and connection.isAlive():
                connection.close()

    return decorated


def get_domains(connection):
    dict = {}
    for id in connection.listDomainsID():
        domain = connection.lookupByID(id)
        dict[domain.name()] = {"status": "run", "id": id,
                               "name": domain.name()}
    for defined_domain in connection.listDefinedDomains():
        dict[defined_domain] = {"status": "shutdown", "id": "-",
                                "name": domain.name()}
    return dict


@libvirt_connection
def start_vm(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] == "start":
            print ("Virtual machine \"" + args.vm_name + " already started.")
        else:
            print ("Starting \"" + args.vm_name + "\"...")
            connection.lookupByName(args.vm_name).create()
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")


@libvirt_connection
def stop_vm(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] == "shutdown":
            print ("Virtual machine \"" + args.vm_name + " is not running.")
        else:
            print ("Try to stop \"" + args.vm_name + "\"...")
            connection.lookupByName(args.vm_name).shutdown()
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")


@libvirt_connection
def forced_stop_vm(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] == "shutdown":
            print ("Virtual machine \"" + args.vm_name + " is not running.")
        else:
            print ("Forced stop \"" + args.vm_name + "\"...")
            connection.lookupByName(args.vm_name).destroy()
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")


@libvirt_connection
def reboot_vm(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] == "shutdown":
            print ("Virtual machine \"" + args.vm_name + " is not running.")
        else:
            print ("Send reboot signal to \"" + args.vm_name + "\"...")
            connection.lookupByName(args.vm_name).reboot()
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")


@libvirt_connection
def show_vm_status(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] == "shutdown":
            print ("Virtual machine \"" + args.vm_name + " is not running.")
        else:
            print ("Virtual machine \"" + args.vm_name + " is running.")
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")


@libvirt_connection
def show_vm_list(args, connection):
    vert_delimiter = "\t| "
    hor_delimiter = "----------------------------------------------------" \
                    "---------------------------"
    print hor_delimiter
    print "id" + vert_delimiter + "Status" + vert_delimiter + "Domain"
    print hor_delimiter
    for domain_name in [domain for domain in get_domains(connection) if
                        domain["status"] != "shutdown"]:
        print domain_name["id"] + vert_delimiter + domain_name[
            "status"] + vert_delimiter + domain_name["name"]
    if args.list_select == "all":
        for domain_name in [domain for domain in get_domains(connection) if
                            domain["status"] == "shutdown"]:
            print domain_name["id"] + vert_delimiter + "shutdown" + \
                + vert_delimiter + domain_name["name"]


@libvirt_connection
def create_vm(args, connection):
    domains = get_domains(connection)
    if args.new_vm_name in domains.keys():
        print ("Virtual machine \"" + args.vm_name + " already created.")
    else:
        domain = Domain(args.new_vm_name, args.memory, args.uuid, args.vcpu,
                        args.os_type, args.type_arch, args.type_machine,
                        args.clock_offset, args.domain_type,
                        args.emulator)
        if args.disks is not None:
            for disk in args.disks:
                domain.add_disk(disk, "disk")
        if args.cdroms is not None:
            for cdrom in args.cdroms:
                domain.add_disk(cdrom, "cdrom")
        if args.nets is not None:
            for net in args.nets:
                domain.add_network(net_name=net)
        if args.bridges is not None:
            for br in args.bridges:
                domain.add_network(type="bridge", net_name=br)

        print ("Try to create \"" + domain.name + "\"")
        connection.defineXML(xml_to_string(domain.get_xml()))


@libvirt_connection
def remove_vm(args, connection):
    domains = get_domains(connection)
    if args.vm_name in domains.keys():
        if get_domains(connection)[args.vm_name]["status"] != "shutdown":
            print ("Forced stop \"" + args.vm_name + "\"...")
            connection.lookupByName(args.vm_name).destroy()
        else:
            print ("Delete \"" + args.vm_name + "\".")
            connection.lookupByName(args.vm_name).destroy()
    else:
        print ("Virtual machine \"" + args.vm_name + " is not created yet.")
