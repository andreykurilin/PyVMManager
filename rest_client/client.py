#!/usr/bin/env python

import manager
from utils.settings import conf
from controller import Controller

__author__ = 'akurilin'


def get_parser():
    parser = manager.get_parser()
    parser.add_argument("-s", "--server", dest="server",
                        help="Connect to the specified REST Server, "
                             "instead of the default connection.",
                        default=conf.Server["address"])
    parser.add_argument("-P", "--port", dest="server_port",
                        help="Connect to the specified REST Server, "
                             "instead of the default connection.",
                        default=conf.Server["port"])
    return parser


def main():
    args = get_parser().parse_args()

    if args.uri is None:
        args.uri = conf.General["uri"]
    if args.handler == "show_info":
            args.handler = "info"
    ctrl = Controller(args.server, args.server_port, args.uri)
    ctrl.all(vars(args))


if __name__ == "__main__":
    main()