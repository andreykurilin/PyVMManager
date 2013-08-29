#!/usr/bin/env python
import wsgi_controller

__author__ = 'akurilin'
_server_address = "127.0.0.1"
_server_port = 8080

if __name__ == '__main__':
    app = wsgi_controller.Controller
    app.add_route("POST", "/start", app.start, ["name"])
    app.add_route("POST", "/stop", app.stop, ["name"])
    app.add_route("POST", "/fstop", app.forced_stop, ["name"])
    app.add_route("POST", "/reboot", app.reboot, ["name"])
    app.add_route("GET", "/list", app.list, ["select"])
    app.add_route("PUT", "/install", app.create, ["name", "memory"])
    app.add_route("DELETE", "/remove", app.remove, ["name"])
    app.add_route("GET", "/info", app.info, ["name"])
    from wsgiref.simple_server import make_server

    server = make_server(_server_address, _server_port, app)
    server.serve_forever()