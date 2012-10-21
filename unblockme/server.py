import logging
import struct

from twisted.internet import defer, protocol, reactor

from unblockme.regex import HOST_FROM_HTTP
from unblockme.client import ProxyClientFactory


class BaseHTTPProxyServer(protocol.Protocol):

    def connectionMade(self):
        if self.factory.validator.valid_client(self.transport.getPeer().host,
                                               self.proto_name):
            self.transport.setTcpKeepAlive(1)
            self.cli_queue = defer.DeferredQueue()
            self.srv_queue = defer.DeferredQueue()
            self.srv_queue.get().addCallback(self.clientDataReceived)
            self.pre_connection_buffer = ''
            self.target_domain_found = False
        else:
            self.transport.loseConnection()

    def connectionLost(self, why):
        self.cli_queue.put(False)

    def clientDataReceived(self, chunk):
        self.transport.write(chunk)
        self.srv_queue.get().addCallback(self.clientDataReceived)

    def dataReceived(self, chunk):
        if self.target_domain_found:
            self.cli_queue.put(chunk)
        else:
            self.pre_connection_buffer += chunk
            domain = self.extract_server_name(self.pre_connection_buffer)
            if domain is not None:
                if self.factory.validator.valid_domain(
                    self.transport.getPeer().host, self.proto_name, domain
                    ):
                    self.target_domain_found = True
                    self.spawnClientConnection(domain)
                else:
                    self.transport.loseConnection()

    def spawnClientConnection(self, domain):
        logging.debug('Spawing client for %s://%s' % (self.proto_name, domain))
        factory = ProxyClientFactory(self.srv_queue, self.cli_queue)
        reactor.connectTCP(domain, self.default_port, factory)
        self.cli_queue.put(self.pre_connection_buffer)


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
        # cut off the tcp header
        packet = chunk[5:]
        i = packet[1 + 3 + 2 + 32 + 1:41]
        if i:
            # jump over the Cipher Suites
            k = struct.unpack(">h", i)[0] + 41
            i = packet[k:k + 1]
            if i:
                # jump over the Compression Methods
                k += struct.unpack(">b", i)[0]
                i = packet[k + 1:k + 3]
                if i:
                    # parse the Extensions list
                    k += 3
                    i = packet[k:k + 2]
                    found = False
                    k += 2
                    while not found:
                        if i == b'\x00\x00':
                            # that's the server name
                            found = True
                            k += 5
                            i = packet[k:k + 2]
                            name_len = struct.unpack(">h", i)[0]
                            name = packet[k + 2:k + 2 + name_len]
                            return name
                        else:
                            # jump over other extension
                            i = packet[k:k + 2]
                            if i:
                                k += struct.unpack(">h", i)[0] + 2
                                i = packet[k:k + 2]
                            else:
                                # server name not found
                                break
        return None


class BaseHTTPProxyServerFactory(protocol.Factory):
    def __init__(self, validator):
        self.validator = validator


class HTTPProxyServerFactory(BaseHTTPProxyServerFactory):
    protocol = HTTPProxyServer


class HTTPSProxyServerFactory(BaseHTTPProxyServerFactory):
    protocol = HTTPSProxyServer
