#!/usr/bin/env python
import argparse
import os
from server.domain_controller.controller import Controller
from server.utils.settings import Settings

__author__ = 'akurilin'
conf = Settings(os.path.join(os.path.dirname(__file__), "settings.ini"))


def get_parser():
    parser = argparse.ArgumentParser(
        description='Py util that help manage'
                    '(create/delete/start/shutdown/reboot) VM.',
        add_help=True)
    action_parser = parser.add_subparsers(metavar="Manage")

    start_parser = action_parser.add_parser('start', help='Start VM')
    start_parser.add_argument('name', help='name of VM')
    start_parser.set_defaults(handler="start")

    stop_parser = action_parser.add_parser('stop', help='Stop VM')
    stop_parser.add_argument('name', help='name of VM')
    stop_parser.set_defaults(handler="stop")

    fstop_parser = action_parser.add_parser('fstop', help='Forced stop VM')
    fstop_parser.add_argument('name', help='name of VM')
    fstop_parser.set_defaults(handler="forced_stop")

    fstop_parser = action_parser.add_parser('reboot', help='Restart VM')
    fstop_parser.add_argument('name', help='name of VM')
    fstop_parser.set_defaults(handler="reboot")

    info_parser = action_parser.add_parser('info', help='Show VM info')
    info_parser.add_argument('name', help='name of VM')
    info_parser.set_defaults(handler="show_info")

    list_parser = action_parser.add_parser('list', help='Displays VM')
    list_parser.add_argument("select", choices=['run', 'all'],
                             metavar="run/all")
    list_parser.set_defaults(handler="list")

    install_parser = action_parser.add_parser('install', help='Install new VM')
    install_parser.add_argument("-n", "--name", dest='name',
                                required=True,
                                help='name of VM', metavar="VM_NAME")
    install_parser.add_argument("-m", "--memory", dest='memory', type=int,
                                help='memory of VM in Bytes', required=True)
    install_parser.add_argument("-u", "--uuid", dest='uuid',
                                help='specify UUID of VM')
    install_parser.add_argument("-v", "--vcpu", dest='vcpu', type=int,
                                help='specify vcpu of VM.',
                                default=conf.Domain["vcpu"])
    install_parser.add_argument("-o", "--os_type", dest='os_type',
                                default=conf.Domain["os_type"],
                                help='specify type of OS.')
    install_parser.add_argument("-t", "--os_type_arch", dest='type_arch',
                                help='specify type of OS.',
                                default=conf.Domain["type_arch"])
    install_parser.add_argument("-T", "--type_machine", dest='type_machine',
                                help='specify type of machine.',
                                default=conf.Domain["type_machine"])
    install_parser.add_argument("-C", "--clock_offset", dest='clock_offset',
                                help='specify clock offset.',
                                default=conf.Domain["clock_offset"])
    install_parser.add_argument("-d", "--domain_type", dest='domain_type',
                                help='specify type of domain. Default=\"kvm\"',
                                default=conf.Domain["domain_type"])
    install_parser.add_argument("-e", "--emulator", dest='emulator',
                                help='specify emulator.',
                                default=conf.Domain["emulator"])
    install_parser.add_argument("-D", "--disk", dest='disks', help='add disk',
                                default=None, nargs='+')
    install_parser.add_argument("-r", "--cdrom", dest='cdroms',
                                help='add cdrom',
                                default=None, nargs='+')
    install_parser.add_argument("-N", "--network", dest='nets',
                                help='add networks',
                                default=None)
    install_parser.add_argument("-b", "--bridge", dest='bridges',
                                help='add bridges',
                                default=None)
    install_parser.set_defaults(handler="create")

    remove_parser = action_parser.add_parser('delete', help='Delete VM')
    remove_parser.add_argument('vm_name', help='name of VM')
    remove_parser.set_defaults(handler="remove")

    parser.add_argument("-c", "--connect", dest="uri",
                        help="Connect to the specified URI, "
                             "instead of the default connection.")
    return parser


def main():
    args = get_parser().parse_args()

    if args.uri is None:
        args.uri = conf.General["uri"]

    dom_controller = Controller(args.uri)
    func = dom_controller.__getattribute__(args.handler)
    func(vars(args))


if __name__ == "__main__":
    main()