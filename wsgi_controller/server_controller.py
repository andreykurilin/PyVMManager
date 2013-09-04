#!/usr/bin/env python
import json

from webob import Request
from domain_controller import controller
from domain_controller.domain import Domain
from domain_controller.controller import NotRunningError
from domain_controller.controller import NotCreatedVMError
from domain_controller.controller import AlreadyCreatedVMError


__author__ = 'akurilin'
_uri = "qemu:///system"


def data_to_dictionary(data):
        request_dict = {}
        for each in str(data).split("&"):
            lst = each.split("=")
            request_dict[lst[0]] = lst[1]
        return request_dict


def ok_200(environ, start_response, message=None):
    start_response('200 Ok', [])
    if message is None:
        return '200'
    else:
        return str(message)


def ok_201(environ, start_response):
    start_response('201 Created', [])
    return '201'


def error_400_response(environ, start_response, message=None):
    start_response('400 Bad Request', [])
    answer = "400"
    if message is not None:
        answer += ": " + message
    return answer


def error_404_response(environ, start_response):
    start_response('404 Not Found', [])
    return '404'


def error_501_response(environ, start_response):
    start_response('501 Not Implemented', [])
    return '501'


class Route(object):
    def __init__(self, req_method, url, func, valid_args):
        self.method = req_method
        self.url = url
        self.func = func
        self.valid_args = valid_args


class Controller(controller.Controller):
    def __init__(self, uri=_uri):
        super(Controller, self).__init__(uri, error_flag=True)
        self.routes = []

    def add_route(self, req_method, url, func, valid_args):
        self.routes.append(Route(req_method, url, func, valid_args))

    def __call__(self, environ, start_response):
        req = Request(environ)
        for route in self.routes:
            if route.method == req.method and route.url == req.path_info:
                for arg in route.valid_args:
                    if arg not in data_to_dictionary(req.body).keys():
                        return error_400_response(environ, start_response,
                                                  "Not enough args.")
                return route.func(environ, start_response)
        return error_404_response(environ, start_response)

    def start(self, environ, start_response):
        req = Request(environ)
        try:
            super(Controller, self).start(data_to_dictionary(req.body))
        except NotCreatedVMError as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response)

    def stop(self, environ, start_response):
        req = Request(environ)
        try:
            super(Controller, self).stop(data_to_dictionary(req.body))
        except (NotCreatedVMError, NotRunningError) as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response)

    def forced_stop(self, environ, start_response):
        req = Request(environ)
        try:
            super(Controller, self). \
                forced_stop(data_to_dictionary(req.body))
        except (NotCreatedVMError, NotRunningError) as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response)

    def reboot(self, environ, start_response):
        req = Request(environ)
        try:
            super(Controller, self). \
                reboot(data_to_dictionary(req.body))
        except (NotCreatedVMError, NotRunningError) as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response)

    def list(self, environ, start_response):
        req = Request(environ)
        domains = self.get_domains_dict()
        args = data_to_dictionary(req.body)
        if "select" in args and args["select"] == "run":
            for key in domains.keys():
                if domains[key]["status"] == "shutdown":
                    domains.pop(key)
        elif "select" in args and args["select"] != "all":
            return error_400_response()
        return ok_200(environ, start_response, json.dumps(domains))

    def create(self, environ, start_response):
        req = Request(environ)
        args = data_to_dictionary(req.body)
        for key in Domain.DEFAULT_VALUES:
            if key not in args:
                args[key] = Domain.DEFAULT_VALUES[key]
        if "disk" in args and "disks" not in args:
            args["disks"] = [].append(args["disk"])
        try:
            super(Controller, self).create(args)
        except AlreadyCreatedVMError as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_201(environ, start_response)

    def remove(self, environ, start_response):
        req = Request(environ)
        try:
            super(Controller, self).remove(data_to_dictionary(req.body))
        except NotCreatedVMError as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response)

    def info(self, environ, start_response):
        req = Request(environ)
        try:
            domain_info = super(Controller, self).\
                info(data_to_dictionary(req.body))
        except NotCreatedVMError as error:
            return error_400_response(environ, start_response, error.__str__())
        return ok_200(environ, start_response, json.dumps(domain_info))