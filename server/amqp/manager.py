#!/usr/bin/env python
import server.amqp.controller as amqp_ctrl
import server.domain_controller.controller as domain_ctrl
from server.utils.settings import conf

__author__ = 'akurilin'


class Controller(amqp_ctrl.Controller):
    _queue = "manage"
    _states = {"start": {"message": "Starting...",
                         "error": domain_ctrl.NotCreatedVMError},
               "stop": {"message": "Try to stop...",
                        "error": domain_ctrl.NotCreatedVMError},
               "forced_stop": {"message": "Forced stop.",
                               "error": domain_ctrl.NotCreatedVMError},
               "reboot": {"message": "Send reboot signal.",
                          "error": domain_ctrl.NotCreatedVMError},
               "create": {"message": "Try to create...",
                          "error": domain_ctrl.AlreadyCreatedVMError},
               "remove": {"message": "Delete",
                          "error": domain_ctrl.NotCreatedVMError},
               "info": {"message": None,
                        "error": domain_ctrl.NotCreatedVMError}}

    def __init__(self):
        super(Controller, self).__init__(Controller._queue)

    def get_domain_ctrl(self, uri):
        return domain_ctrl.Controller(uri, error_flag=True)

    def list(self, args):
        dom_ctrl = self.get_domain_ctrl(args["uri"])
        domains = dom_ctrl.get_domains_dict()
        if args["select"] == "run":
            for name in domains.keys():
                if domains[name]["status"] == "shutdown":
                    domains.pop(name)
        return domains

    def _ctrl_do(self, args):
        dom_ctrl = self.get_domain_ctrl(args["uri"])
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