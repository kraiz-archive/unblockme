import logging
import struct

from twisted.internet import defer, protocol, reactor

from unblockme.regex import HOST_FROM_HTTP
from unblockme.client import ProxyClientFactory
from unblockme.tls import ClientHello


class BaseHTTPProxyServer(protocol.Protocol):

    def connectionMade(self):
        if self.factory.validator.valid_client(self.transport.getPeer().host, self.proto_name):
            self.cli_queue = defer.DeferredQueue()
            self.srv_queue = defer.DeferredQueue()
            self.srv_queue.get().addCallback(self.clientDataReceived)
            self.target_domain_found = False
        else:
            self.transport.loseConnection()

    def connectionLost(self, why):
        self.cli_queue.put(False)

    def clientDataReceived(self, chunk):
        self.transport.write(chunk)
        self.srv_queue.get().addCallback(self.clientDataReceived)

    def dataReceived(self, chunk):
        if not self.target_domain_found:
            domain = self.extract_server_name(chunk)
            logging.debug('Parsed server name from request: %s' % domain)
            if domain is None:
                logging.error('Seems client send no TLS SNI Extension')
                self.transport.loseConnection()
            elif not self.factory.validator.valid_domain(
                self.transport.getPeer().host, self.proto_name, domain
                ):
                # logging done by validator
                self.transport.loseConnection()
            else:
                # we're fine
                self.target_domain_found = True
                self.spawnClientConnection(domain)
        self.cli_queue.put(chunk)

    def spawnClientConnection(self, domain):
        logging.debug('Spawing client for %s://%s' % (self.proto_name, domain))
        factory = ProxyClientFactory(self.srv_queue, self.cli_queue)
        reactor.connectTCP(domain, self.default_port, factory)


class HTTPProxyServer(BaseHTTPProxyServer):
    default_port = 80
    proto_name = 'http'

    def extract_server_name(self, chunk):
        result = HOST_FROM_HTTP.search(chunk)
        return None if result is None else result.groups()[0]


class HTTPSProxyServer(BaseHTTPProxyServer):
    default_port = 443
    proto_name = 'https'

    def extract_server_name(self, chunk):
        return ClientHello(chunk).get_server_name()


class BaseHTTPProxyServerFactory(protocol.Factory):
    def __init__(self, validator):
        self.validator = validator


class HTTPProxyServerFactory(BaseHTTPProxyServerFactory):
    protocol = HTTPProxyServer


class HTTPSProxyServerFactory(BaseHTTPProxyServerFactory):
    protocol = HTTPSProxyServer
