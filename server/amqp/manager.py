#!/usr/bin/env python
from server.amqp.controller import Controller as AQMPController
from server.domain_controller.controller import Controller as DOMController
from server.domain_controller.controller import NotCreatedVMError, \
    AlreadyCreatedVMError

from server.utils.settings import conf

__author__ = 'akurilin'


class Controller(AQMPController):
    _queue = "manage"
    _states = {"start": {"message": "Starting...", "error": NotCreatedVMError},
               "stop": {"message": "Try to stop...",
                        "error": NotCreatedVMError},
               "forced_stop": {"message": "Forced stop.",
                               "error": NotCreatedVMError},
               "reboot": {"message": "Send reboot signal.",
                          "error": NotCreatedVMError},
               "create": {"message": "Try to create...",
                          "error": AlreadyCreatedVMError},
               "remove": {"message": "Delete",
                          "error": NotCreatedVMError},
               "info": {"message": None,
                          "error": NotCreatedVMError}}

    def __init__(self):
        super(Controller, self).__init__(Controller._queue, True)

    def get_dom_ctrl(self, uri):
        return DOMController(uri, error_flag=True)

    def list(self, args):
        dom_ctrl = self.get_dom_ctrl(args["uri"])
        domains = dom_ctrl.get_domains_dict()
        if args["select"] == "run":
            for name in domains.keys():
                if domains[name]["status"] == "shutdown":
                    domains.pop(name)
        return domains

    def _ctrl_do(self, args):
        dom_ctrl = self.get_dom_ctrl(args["uri"])
        try:
            result = dom_ctrl.__getattribute__(args["handler"])(args)
        except Controller._states[args["handler"]]["error"] as error:
            return error
        if Controller._states[args["handler"]]["message"] is None:
            return result
        return Controller._states[args["handler"]]["message"]

    def __getattr__(self, item):
        if item == "list":
            return self.list
        if item in Controller._states.keys():
            return self._ctrl_do


def main():
    ctrl = Controller()
    ctrl.start_consuming()

if __name__ == "__main__":
    main()