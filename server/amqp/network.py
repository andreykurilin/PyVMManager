#!/usr/bin/env python
import server.amqp.controller as amqp_controller
import server.db.controller as db_controller
from server.db.tables import IPAddr

__author__ = 'akurilin'


class Controller(amqp_controller.Controller):
    _queue = "network"

    def __init__(self):
        super(Controller, self).__init__(Controller._queue, no_ack=True)

    def get_db_controller(self):
        return db_controller.Controller()

    def add_address(self, args):
        controller = self.get_db_controller()
        addresses = controller.get_addresses()
        if args["address"] not in addresses.keys():
            controller.add_record(IPAddr(args["address"]))

    def add_addresses(self, args):
        start_ip, end_ip = args["addresses"].split("-")
        for address in range(start_ip, end_ip):
            self.add_address({"address": address})

    def __getattr__(self, item):
        if item == "add":
            return self.add_address
        elif item == "add-range":
            return self.add_addresses


def main():
    ctrl = Controller()
    ctrl.start_consuming()

if __name__ == "__main__":
    main()