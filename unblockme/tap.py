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

    # parse config & log
    interface = config['interface']
    logging.info('Starting unblockme at %s' % interface)

    clients = config['clients'].split(',')
    logging.info('clients: %' % ', '.join(clients))

    domains = config['domains'].split(',')
    logging.info('domains: %' % ', '.join(domains))

    forward_dns = config['forward-dns'].split(',')
    logging.info('forward-dns: %' % ', '.join(domains))

    # validator
    validator = Validator(clients=clients, domains=domains)

    # dns instanciation
    dns_resolver = MappingResolver(
        mapping=dict((d, interface) for d in domains),
        servers=[(ip, 53) for ip in forward_dns]
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
