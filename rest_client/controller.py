#!/usr/bin/env python
from prettytable import PrettyTable
import requests
from utils.settings import conf

__author__ = 'akurilin'

_status = {
    200: "Ok",
    201: "Created",
    400: "Bad Request",
    404: "Not Found",
    501: "Not Implemented"
}


def print_status(status, message=None):
    print "{0} {1}".format(status, _status[status])
    if message is not None:
        print message


class Controller(object):
    _handler = {
        "list": requests.get,
        "info": requests.get,
        "install": requests.put,
        "remove": requests.put,
        "else": requests.post
    }

    def __init__(self, address, port, uri=conf.General["uri"]):
        self.address = address
        self.port = int(port)

    def all(self, args):

        req_url = "http://{0}:{1}/{2}".format(self.address, self.port,
                                              args["handler"])
        if args["handler"] not in Controller._handler.keys():
            request_func = Controller._handler["else"]
        else:
            request_func = Controller._handler[args["handler"]]
        req = request_func(req_url, data=args)
        print_status(req.status_code)
        if args["handler"] == "info":
            self.print_info(eval(req.text))
        elif args["handler"] == "list":
            self.print_list(eval(req.text))

    def print_info(self, info):
        info_table = PrettyTable(["Name", "UUID", "State", "Memory", "VCPU"])
        info_table.padding_width = 1
        info_table.add_row([info["name"], info["uuid"], info["state"],
                            info["memory"], info["vcpu"]])
        print info_table

    def print_list(self, info):
        list_table = PrettyTable(["id", "Name", "Status"])
        list_table.align["Name"] = "l"
        list_table.padding_width = 1
        for dom in info.values():
            list_table.add_row([dom["id"], dom["name"], dom["status"]])
        print list_table