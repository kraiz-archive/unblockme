#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='unblockme',
    version='0.0.2',
    author='Lars Kreisz',
    author_email='der.kraiz@gmail.com',

    packages=['unblockme'],
    data_files=[
        ('twisted/plugins', ['twisted/plugins/unblockme_plugin.py']),
        ('/etc/',           ['deploy/unblockme.conf']),
        ('/etc/init.d',     ['deploy/unblockme'])
    ]
)
