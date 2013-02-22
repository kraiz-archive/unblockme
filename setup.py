#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name='unblockme',
    version='0.1.0',
    packages=['unblockme'],
    url='https://dev.kraiz.de/projects/unblockme',
    license='MIT',
    author='kraiz',
    author_email='dev@kraiz.de',
    description='proxy software against geoblocking',
    install_requires=[
        'gevent>=0.13',
        'dnslib>=0.8.2'
    ],
    entry_points = {
        'console_scripts': [
            'unblockme = unblockme:main',
        ],
    }
)
