#!/usr/bin/env python
import os
import sys
import pyvm_install
import pyvm_control

__author__ = 'akurilin'


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


# Check arguments
if sys.argv.__len__() > 1:
    if sys.argv[1] in ("-h", "--help"):
        usage()
    elif sys.argv[1] in ("-a", "--author"):
        print_author()
    elif sys.argv[1] in ("install", "create", "add"):
        pyvm_install.create(sys.argv[2:])
    elif sys.argv[1] in ("remove", "rm", "delete", "del"):
        pyvm_install.remove(sys.argv[2:])
    elif sys.argv[1] in ("start", "on", "stop", "down", "reboot", "restart"):
        pyvm_control.__main__(sys.argv[2:])
else:
    usage()
