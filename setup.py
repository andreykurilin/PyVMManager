#!/usr/bin/env python

__author__ = 'akurilin'

from setuptools import setup, find_packages

setup(
    name='PyVMManager',
    version='1.3',
    description="Py util that help manage"
                "(create/delete/start/shutdown/reboot) VM.",
    author=__author__,
    packages=find_packages(),
    py_modules=['manager', 'sql_update_daemon'],
    entry_points={
        'console_scripts': [
            'pyvm-manager = manager:main',
            'pyvm-server = rest_server.server:main',
            'pyvm-rest = rest_client.client:main',
            'pyvmd = sql_update_daemon:main',
        ]
    },
    platforms='any',
    zip_safe=False,
    include_package_data=True,
    requires=['webob', 'sqlalchemy', 'requests', 'prettytable'],
)