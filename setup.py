#!/usr/bin/env python

__author__ = 'akurilin'

from setuptools import setup, find_packages

setup(
    name='PyVMManager',
    version='1.6',
    description="Py util that help manage"
                "(create/delete/start/shutdown/reboot) VM.",
    author=__author__,
    packages=find_packages(),
    data_files=[('/etc/pyvm/', ['settings.ini'])],
    entry_points={
        'console_scripts': [
            'pyvm-manager = client.cli_manager:main',
            'pyvm-manager-rest = client.rest.manager:main',
            'pyvm-rest-server = server.rest.serv:main',
            'pyvmd = server.update_daemon:main',
        ]
    },
    platforms='any',
    zip_safe=False,
    include_package_data=True,
    requires=['webob', 'sqlalchemy', 'requests', 'prettytable', 'alembic',
              'pika'],
)