#!/usr/bin/env python
from webob import Request
from wsgi_controller import controller

__author__ = 'akurilin'


class Route(object):
    def __init__(self, req_method, url, func):
        self.method = req_method
        self.url = url
        self.func = func


class Router(object):
    def __init__(self):
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


