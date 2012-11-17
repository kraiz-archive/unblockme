#!/usr/bin/env python
from setuptools import setup

setup(
    name='unblockme',
    version='0.0.2',
    author='Lars Kreisz',
    author_email='der.kraiz@gmail.com',

    packages=['unblockme'],
    data_files=[
        ('twisted/plugins', ['twisted/plugins/unblockme_plugin.py']),
        ('/etc/', ['deploy/unblockme.conf']),
        ('/etc/init.d', ['deploy/unblockme'])
    ],

    install_requires=['Twisted>=11']
)
