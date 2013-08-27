#!/usr/bin/env python

__author__ = 'akurilin'
_uri = "qemu:///system"

def error_404(environ, start_response):
    start_response('404 Not Found', [])
    return '404'


def ok_200(environ, start_response):
    start_response('200 Ok', [])
    return '200'


def start_vm(environ, start_response):
    pass


class Controller(object):
    pass