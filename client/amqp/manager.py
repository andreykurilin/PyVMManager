#!/usr/bin/env python
from client import cli_manager
from client.amqp.controller import Controller
from server.utils.settings import conf

__author__ = 'akurilin'


def get_parser():
    parser = cli_manager.get_parser()
    parser.add_argument("-a", "--amqp-host", dest="amqp_host",
                        help="Connect to the specified AMQP host.",
                        default=conf.AMQP["host"])
    return parser


def main():
    args = get_parser().parse_args()

    if args.uri is None:
        args.uri = conf.General["uri"]
    if args.handler == "show_info":
            args.handler = "info"
    ctrl = Controller(args.amqp_host)
    result = ctrl.call(vars(args))
    if vars(args)["handler"] == "info":
        ctrl.print_info(result)
    elif vars(args)["handler"] == "list":
        ctrl.print_list(result)
    else:
        print result

if __name__ == "__main__":
    main()