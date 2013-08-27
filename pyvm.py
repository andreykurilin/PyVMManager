#!/usr/bin/env python
import argparse
from domain_controller.controller import *

__author__ = 'akurilin'
__version__ = "1.0 Alpha"

_uri = "qemu:///system"

def main():
    parser = argparse.ArgumentParser(
        description='Py util that help manage'
                    '(create/delete/start/shutdown/reboot) VM.')
    parser = argparse.ArgumentParser(add_help=True, version=__version__)
    action_parser = parser.add_subparsers(metavar="Manage")

    start_parser = action_parser.add_parser('start', help='Start VM')
    start_parser.add_argument('vm_name', help='name of VM')
    start_parser.set_defaults(handler=start_vm)

    stop_parser = action_parser.add_parser('stop', help='Stop VM')
    stop_parser.add_argument('vm_name', help='name of VM')
    stop_parser.set_defaults(handler=stop_vm)

    fstop_parser = action_parser.add_parser('fstop', help='Forced stop VM')
    fstop_parser.add_argument('vm_name', help='name of VM')
    fstop_parser.set_defaults(handler=forced_stop_vm)

    fstop_parser = action_parser.add_parser('reboot', help='Restart VM')
    fstop_parser.add_argument('vm_name', help='name of VM')
    fstop_parser.set_defaults(handler=reboot_vm)

    stop_parser = action_parser.add_parser('status', help='Show status VM')
    stop_parser.add_argument('vm_name', help='name of VM')
    stop_parser.set_defaults(handler=show_vm_status)

    list_parser = action_parser.add_parser('list', help='Displays VM')
    list_parser.add_argument("list_select", choices=['run', 'all'],
                             metavar="run/all")
    list_parser.set_defaults(handler=show_vm_list)

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
    install_parser.add_argument("-D", "--disk", dest='disks', help='add disk',
                                default=None, nargs='+')
    install_parser.add_argument("-r", "--cdrom", dest='cdroms', help='add cdrom',
                                default=None, nargs='+')
    install_parser.add_argument("-N", "--network", dest='nets',
                                help='add networks',
                                default=None, nargs='+')
    install_parser.add_argument("-b", "--bridge", dest='bridges',
                                help='add bridges',
                                default=None, nargs='+')
    install_parser.set_defaults(handler=create_vm)

    remove_parser = action_parser.add_parser('delete', help='Delete VM')
    remove_parser.add_argument('vm_name', help='name of VM')
    remove_parser.set_defaults(handler=remove_vm)

    parser.add_argument("-c", "--connect", dest="uri",
                        help="Connect to the specified URI, "
                             "instead of the default connection.")
    args = parser.parse_args()

    if args.uri is None:
        args.uri = _uri

    args.handler(args)

if __name__ == "main":
    main()