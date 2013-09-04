#!/usr/bin/env python
import requests
from settings import conf

__author__ = 'akurilin'


_status = {
    200: "Ok",
    201: "Created",
    400: "Bad Request",
    404: "404 Not Found",
    501: "Not Implemented"
}


def print_status(status, message=None):
    print "{0} {1}".format(status, _status[status])
    if message is not None:
        print message


class Controller(object):
    def __init__(self, address, port, uri=conf.General["uri"]):
        self.address = address
        self.port = int(port)

    def start(self, args):
        req_url = "http://{0}:{1}/start".format(self.address, self.port)
        req = requests.post(req_url, data=args)
        if req.status_code == 400:
            print_status(req.status_code, "Virtual machine is not created yet")
        elif req.status_code == 200:
            print_status(req.status_code, "Starting...")

    def stop(self, environ, start_response):
        pass

    def forced_stop(self, environ, start_response):
        pass

    def reboot(self, environ, start_response):
        pass

    def list(self, environ, start_response):
        pass

    def create(self, environ, start_response):
        pass

    def remove(self, environ, start_response):
        pass

    def info(self, environ, start_response):
        pass