#!/usr/bin/env python
import argparse
from client.amqp.controller import Controller
from server.utils.settings import conf

__author__ = 'akurilin'


def get_parser():
    parser = argparse.ArgumentParser(
        description='Py util that added addresses to PyVMManager db.',
        add_help=True)
    action_parser = parser.add_subparsers(metavar="Manage")

    address_parser = action_parser.add_parser('add', help='Add address')
    address_parser.add_argument('address', help='ip address')
    address_parser.set_defaults(handler="add")

    addresses_parser = action_parser.add_parser('add-range',
                                            help='Add range of addresses')
    addresses_parser.add_argument('addresses', help='Range of ip addresses')
    addresses_parser.set_defaults(handler="add_range")

    parser.add_argument("-c", "--connect", dest="uri",
                        help="Connect to the specified URI, "
                             "instead of the default connection.")
    parser.add_argument("-a", "--amqp-host", dest="amqp_host",
                        help="Connect to the specified AMQP host.",
                        default=conf.AMQP["host"])
    return parser


def main():
    args = get_parser().parse_args()

    if args.uri is None:
        args.uri = conf.General["uri"]

    ctrl = Controller(args.amqp_host, respond=False)
    result = ctrl.call(vars(args))
    if result is None:
        print "done."

if __name__ == "__main__":
    main()