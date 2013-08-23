#!/usr/bin/env python
import argparse
from domain_controller import *

__author__ = 'akurilin'
__version__ = "1.0 Alpha"

_uri = "qemu:///system"

def handler_control(args):
    control(args.control_action, args.vm_name, _uri)


parser = argparse.ArgumentParser(
    description='Py util that help manage'
                '(create/delete/start/shutdown/reboot) VM.')
parser = argparse.ArgumentParser(add_help=True, version=__version__)
action_parser = parser.add_subparsers(metavar="Manage")
control_parser = action_parser.add_parser('status',
                                          help='Show or change status of VM')
control_parser.add_argument('vm_name', help='name of VM')
control_parser.add_argument("--action", dest="control_action",
                            choices=["start", "stop", "reboot",
                                     "fstop"], default="start",
                            help="action", metavar="ACTION")
control_parser.set_defaults(handler=handler_control)

list_parser = action_parser.add_parser('list', help='Displays VM')
list_parser.add_argument("list_select", choices=['run', 'all'],
                         metavar="run/all")
list_parser.set_defaults(handler=handler_control)


install_parser = action_parser.add_parser('install', help='Install new VM')
install_parser.add_argument("-n", "--name", dest='new_vm_name', required=True,
                            help='name of VM', metavar="VM_NAME")
install_parser.add_argument("-m", "--memory", dest='memory', type=int,
                            help='memory of VM in Bytes', required=True)
install_parser.add_argument("-u", "--uuid", dest='uuid',
                            help='specify UUID of VM')
install_parser.add_argument("-v", "--vcpu", dest='vcpu', type=int,
                            help='specify vcpu of VM. Default=1', default=1)
install_parser.add_argument("-o", "--os_type", dest='os_type', default="hvm",
                            help='specify type of OS. Default=\"hvm\"')
install_parser.add_argument("-t", "--os_type_arch", dest='type_arch',
                            help='specify type of OS. Default=\"x86_64\"',
                            default="x86_64")
install_parser.add_argument("-T", "--type_machine", dest='type_machine',
                            help='specify type of machine. Default=\"pc-1.0\"',
                            default="pc-1.0")
install_parser.add_argument("-C", "--clock_offset", dest='clock_offset',
                            help='specify clock offset. Default=\"utc\"',
                            default="utc")
install_parser.add_argument("-d", "--domain_type", dest='domain_type',
                            help='specify type of domain. Default=\"kvm\"',
                            default="kvm")
install_parser.add_argument("-e", "--emulator", dest='emulator',
                            help='specify emulator. Default=\"/usr/bin/kvm\"',
                            default="/usr/bin/kvm")
install_parser.set_defaults(handler=handler_control)

parser.add_argument("-c", "--connect", dest="uri",
                    help="Connect to the specified URI, "
                         "instead of the default connection.")
args = parser.parse_args()

args.handler(args)

if "uri" in args:
    _uri = args.uri
if "vm_name" in args:
    control(args.control_action, args.vm_name, _uri)
elif "list_select" in args:
    show(args.list_select, _uri)
elif "new_vm_name" in args:
    pass
else:
    parser.print_help()