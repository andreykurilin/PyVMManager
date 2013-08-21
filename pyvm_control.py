#!/usr/bin/env python

import libvirt
import os
import sys

__author__ = 'akurilin'
__uri__ = "qemu:///system"


# Print how to use this program
def usage():
    print (os.path.basename(__file__) + " [OPTION]")
    print ("\n\tOPTIONS:")
    print ("\t\t-h, --help"
           "\n\t\t\tprint help")
    print ("\t\t-a, --author"
           "\n\t\t\tprint author")
    sys.exit()


# Print information about author
def print_author():
    print ("Author: " + __author__)
    sys.exit()


# Return dictionary, where key is ID of running domains and Value is a domain name
def get_running_domains(uri=__uri__):
    dict = {}
    connection = libvirt.open(uri)
    try:
        for id in connection.listDomainsID():
            dict[id] = connection.lookupByID(id).name()
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()
    return dict


# Return list of offline domains
def get_offline_domains(uri=__uri__):
    connection = libvirt.open(uri)
    try:
        defined_domains = connection.listDefinedDomains()
        if defined_domains.__len__() == 0:
            return []
        else:
            return defined_domains
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Print list of VMs
def print_list(key="None"):
    delimiter = "\t|\t"
    print "id" + delimiter + "Status" + delimiter + "Domain\n----------------------------------------------------"
    # print running VMs
    dict = get_running_domains()
    if dict.__len__() != 0:
        for id in dict.keys():
            print str(id) + delimiter + "Running" + delimiter + dict[id]

    # print offline VMs
    if key != "run":
        offline_domains = get_offline_domains()
        if offline_domains.__len__() != 0:
            for domain_name in offline_domains:
                print "-" + delimiter + "Offline" + delimiter + domain_name


# Start VM
def start(args, uri=__uri__):
    try:
        connection = libvirt.open(uri)
        if args.__len__() == 1:
            connection.lookupByName(args[0]).create()
        else:
            usage()
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Shutdown VM
def shutdown(args, uri=__uri__):
    try:
        connection = libvirt.open(uri)
        if args.__len__() == 1:
            connection.lookupByName(args[0]).shutdown()
        else:
            usage()
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Forced stop VM
def stop(args, uri=__uri__):
    try:
        connection = libvirt.open(uri)
        if args.__len__() == 1:
            connection.lookupByName(args[0]).destroy()
        else:
            usage()
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Restart VM
def restart(args, uri=__uri__):
    try:
        connection = libvirt.open(uri)
        if args.__len__() == 1:
            connection.lookupByName(args[0]).reboot()
        else:
            usage()
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Check arguments
if sys.argv.__len__() == 1:
    print_list()
elif sys.argv.__len__() > 1:
    if sys.argv[1] in ("-h", "--help"):
        usage()
    elif sys.argv[1] in ("-a", "--author"):
        print_author()
    elif sys.argv[1] == "run":
        print_list("run")
    elif sys.argv[1] in ("start", "on"):
        start(sys.argv[2:])
    elif sys.argv[1] in ("stop", "down", "shutdown"):
        shutdown(sys.argv[2:])
    elif sys.argv[1] in ("fstop", "stop!", "fdown", "down!", "fshutdown", "shutdown!"):
        stop(sys.argv[2:])
    elif sys.argv[1] in ("reboot", "restart"):
        restart(sys.argv[2:])
else:
    usage()