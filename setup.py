#!/usr/bin/env python
from distutils.core import setup


def refresh_plugin_cache():
    from twisted.plugin import IPlugin, getPlugins
    list(getPlugins(IPlugin))


if __name__ == '__main__':
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

        install_requires=['Twisted>=11']
    )

refresh_plugin_cache()
