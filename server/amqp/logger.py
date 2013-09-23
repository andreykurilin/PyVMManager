#!/usr/bin/env python
from server.amqp.controller import Controller as AQMPController
from server.utils.settings import conf
from datetime import datetime

__author__ = 'akurilin'


class Controller(AQMPController):
    _queue = "log"

    def __init__(self):
        super(Controller, self).__init__(Controller._queue, no_ack=True)

    def logging(self, args):
        try:
            f = open(conf.AMQP["log_file"], "a")
            cur_time = str(datetime.now())
            f.write("[{0}] Received \'{1}\' request : {2}\n"\
                    .format(cur_time, args["handler"], args))
            f.close()
        except IOError as er:
            print er

    def __getattr__(self, item):
        if item in ("start", "stop", "forced_stop", "reboot", "create",
                    "remove", "info", "list", "add", "add-range"):
            return self.logging


def main():
    ctrl = Controller()
    ctrl.start_consuming()


if __name__ == "__main__":
    main()