from setuptools import setup

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
        'gevent==1.0dev',
        'dnslib>=0.8.2',
        'psutil>=0.6.1'
    ],
    dependency_links=[
        'https://github.com/SiteSupport/gevent/tarball/master#egg=gevent-1.0dev',
    ],
    entry_points={
        'console_scripts': [
            'unblockme = unblockme:main',
        ],
    }
)
