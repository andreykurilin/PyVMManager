#!/usr/bin/env python

__author__ = 'akurilin'

from setuptools import setup, find_packages

setup(
    name='PyVMManager',
    version='1.1',
    description="Py util that help manage"
                "(create/delete/start/shutdown/reboot) VM.",
    author=__author__,
    namespace_packages=['pyvm'],
    packages=find_packages(),
    py_modules=['pyvm', 'xml_utils', 'settings', 'pyvm_server',
                'wsgi_controller'],
    entry_points={
        'console_scripts': [
            'pyvm-manager = pyvm:main',
            'pyvm-wsgi = pyvm_server:main',
        ]
    },
    platforms='any',
    zip_safe=False,
    include_package_data=True,
    requires=['webob', 'sqlalchemy'],
)