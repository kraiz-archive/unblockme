#!/usr/bin/env python
from setuptools import setup


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


if __name__ == '__main__':
    setup(
        name='unblockme',
        version='0.0.3',
        author='Lars Kreisz',
        author_email='der.kraiz@gmail.com',

        packages=['unblockme', 'twisted.plugins'],
        package_data={
            'twisted': ['plugins/unblockme_plugin.py'],
        },
        data_files=[
            ('/etc/', ['deploy/unblockme.conf']),
            ('/etc/init.d', ['deploy/unblockme'])
        ],

        install_requires=['Twisted>=11']
    )

refresh_plugin_cache()
