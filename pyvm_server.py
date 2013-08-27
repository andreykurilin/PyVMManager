#!/usr/bin/env python
from wsgi_controller.router import Router
from wsgi_controller.controller import *

__author__ = 'akurilin'
_server_address = "127.0.0.1"
_server_port = 8080


if __name__ == '__main__':
    app = Router()
    app.add_route("GET", "/url", error_404)
    app.add_route("GET", "/create", ok_200)
    from wsgiref.simple_server import make_server
    server = make_server(_server_address, _server_port, app)
    server.serve_forever()