#!/usr/bin/env python
from webob import Request

__author__ = 'akurilin'
_uri = "qemu:///system"

from domain_controller import controller


def error_404(environ, start_response):
    start_response('404 Not Found', [])
    return '404'


def ok_200(environ, start_response):
    start_response('200 Ok', [])
    return '200'


def start_vm(environ, start_response):
    pass


class Route(object):
    def __init__(self, req_method, url, func):
        self.method = req_method
        self.url = url
        self.func = func


class Controller(controller.Controller):
    @staticmethod
    def data_to_dic(data):
        dic = {}
        for each in str(data).split("&"):
            lst = each.split("=")
            dic[lst[0]] = lst[1]
        return dic

    def __init__(self, uri=_uri):
        super(Controller, self).__init__(uri, error_flag=True, Namespace=False)
        self.routes = []

    def add_route(self, req_method, url, func):
        self.routes.append(Route(req_method, url, func))

    def __call__(self, environ, start_response):
        req = Request(environ)

        for route in self.routes:
            if route.method == req.method \
                    and route.url == req.path_info:
                return route.func(environ, start_response)
        return controller.error_404(environ, start_response)

    def start_vm(self, environ, start_response):
        req = Request(environ)

        return super(Controller, self).start_vm(req.body)