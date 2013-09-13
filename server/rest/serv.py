#!/usr/bin/env python

from server.utils.settings import conf
from server.rest.controller import Controller

__author__ = 'akurilin'
_server_address = conf.Server["address"]
_server_port = int(conf.Server["port"])


def main():
    app = Controller()
    app.add_route("POST", "/start", app.start, ["name"])
    app.add_route("POST", "/stop", app.stop, ["name"])
    app.add_route("POST", "/fstop", app.forced_stop, ["name"])
    app.add_route("POST", "/reboot", app.reboot, ["name"])
    app.add_route("GET", "/list", app.list, ["select"])
    app.add_route("PUT", "/install", app.create, ["name", "memory"])
    app.add_route("DELETE", "/remove", app.remove, ["name"])
    app.add_route("GET", "/info", app.info, ["name"])
    from wsgiref.simple_server import make_server

    serv = make_server(_server_address, _server_port, app)
    serv.serve_forever()

if __name__ == '__main__':
    main()