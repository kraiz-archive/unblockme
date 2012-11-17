#!/usr/bin/env python
import sys

from distutils.core import setup
from distutils.command.install_data import install_data


class post_install(install_data):
    def run(self):
        install_data.run(self)
        print "ARGV: " + sys.argv[1]

setup(
    name='unblockme',
    version='0.0.2a1',
    author='Lars Kreisz',
    author_email='der.kraiz@gmail.com',

    packages=['unblockme', 'twisted.plugins'],
    package_data={
        'twisted': ['plugins/unblockme_plugin.py'],
        'unblockme': ['deploy/unblockme.conf',
                      'deploy/unblockme']
    },
    data_files=[
        ('/etc/', ['unblockme/deploy/unblockme.conf']),
        ('/etc/init.d', ['unblockme/deploy/unblockme'])
    ],

    install_requires=['Twisted>=11'],
    cmdclass=dict(install=post_install)
)
