#!/usr/bin/env python
import libvirt
import os
import sys
from Domain import Domain

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


# Create VM
def create(vm_name, memory, img_address, img_type="none", uuid=None, vcpu=1, os_type="hvm", type_arch="x86_64",
           type_machine="pc-1.0", clock_offset="utc",
           domain_type="kvm", emulator="/usr/bin/kvm", network_type="network", network="default", mac_address=None,
           uri=__uri__):
    connection = libvirt.open(uri)
    try:
        dsk = Domain(vm_name, memory, img_address,
                     img_type, uuid, vcpu, os_type, type_arch, type_machine, clock_offset, domain_type, emulator,
                     network_type, network, mac_address)
        connection.defineXML(dsk.get_xml())
    except libvirt.libvirtError:
        print "Can't connect to URI"
        sys.exit()
    finally:
        connection.close()


# Remove VM
def remove(param):
    pass


# Check arguments
if sys.argv.__len__() > 1:
    if sys.argv[1] in ("-h", "--help"):
        usage()
    elif sys.argv[1] in ("-a", "--author"):
        print_author()
    elif sys.argv[1] in ("del", "delete", "rm", "remove"):
        remove(sys.argv[2:])
    else:
        if sys.argv.__len__() < 4:
            usage()
        elif sys.argv.__len__() == 4:
            create(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            for i in range(4, sys.argv.__len__()):
                pass
            create(sys.argv[1], sys.argv[2], sys.argv[3])
else:
    usage()