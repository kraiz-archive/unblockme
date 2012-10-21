import logging

from twisted.application import service
from twisted.application.internet import TCPServer, UDPServer
from twisted.names import server, cache
from twisted.python import usage

from unblockme.auth import Validator
from unblockme.dns import AuthedDNSDatagramProtocol
from unblockme.resolver import MappingResolver
from unblockme.server import HTTPProxyServerFactory, HTTPSProxyServerFactory


# dedicated logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    filename='/var/log/unblockme.log')


class Options(usage.Options):
    optParameters = [
        ['interface', 'i', '192.168.178.38'],
        ['clients', 'c', 'home.kraiz.de,hostwindows'],
        ['domains', 'd', '.netflix.com'],
        ['forward-dns', 'dns', '8.8.8.8'],
    ]


def makeService(config):
    unblockme_service = service.MultiService()

    # validator
    validator = Validator(clients=config['clients'].split(','),
                          domains=config['domains'].split(','))

    # dns instanciation
    dns_resolver = MappingResolver(
        mapping=dict((d, config['interface'])
                     for d in config['domains'].split(',')),
        servers=[(ip, 53) for ip in config['forward-dns'].split(',')]
    )
    dns_factory = server.DNSServerFactory(clients=[dns_resolver],
                                          caches=[cache.CacheResolver()])
    dns_protocol = AuthedDNSDatagramProtocol(controller=dns_factory,
                                             validator=validator)

    # http + https proxy instanciation
    http_factory = HTTPProxyServerFactory(validator=validator)
    https_factory = HTTPSProxyServerFactory(validator=validator)

    # stack anything together
    UDPServer(53, dns_protocol).setServiceParent(unblockme_service)
    TCPServer(80, http_factory).setServiceParent(unblockme_service)
    TCPServer(443, https_factory).setServiceParent(unblockme_service)

    return unblockme_service
