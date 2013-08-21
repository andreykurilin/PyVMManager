#!/usr/bin/env python
import os
import sys

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


# Create VM
def create(param):
    pass


# Check arguments
if sys.argv.__len__() > 1:
    if sys.argv[1] in ("-h", "--help"):
        usage()
    elif sys.argv[1] in ("-a", "--author"):
        print_author()
else:
    create(sys.argv[1:])