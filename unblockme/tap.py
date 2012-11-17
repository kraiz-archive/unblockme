import ConfigParser
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
#        ['interface', 'i', '199.195.249.85'],
#        ['clients', 'c', 'home.kraiz.de'],
#        ['domains', 'd', '.netflix.com,.grooveshark.com'],
#        ['forward-dns', 'dns', '8.8.8.8'],
    ]


def makeService(config):
    unblockme_service = service.MultiService()
    
    # parse config & log
    cfg = ConfigParser.ConfigParser()
    cfg.read('/etc/unblockme.conf')

    interface = cfg.get('unblockme', 'bind-address')
    logging.info('Starting unblockme at %s' % interface)

    clients = [s.strip() for s in cfg.get('unblockme', 'clients').split(',')]
    logging.info('clients: %s' % ', '.join(clients))

    domains = [s.strip() for s in cfg.get('unblockme', 'domains').split(',')]
    logging.info('domains: %s' % ', '.join(domains))

    forward_dns = [s.strip() for s in cfg.get('unblockme', 'forward-dns').split(',')]
    logging.info('forward-dns: %s' % ', '.join(forward_dns))

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
