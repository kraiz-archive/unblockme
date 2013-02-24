import logging

from gevent.server import StreamServer
from gevent.socket import create_connection

from unblockme.forwarder import DuplexForwarder
from unblockme.regex import HOST_FROM_HTTP
from unblockme.tls import ClientHello


class BaseProxy(StreamServer):
    buffer_size = 2 ** 18
    timeout = 5

    logger = None
    port = None

    def handle(self, source, address):
        destination_host, buf = self.buffer_until_host_known(source)
        self.logger.debug('host resolved to %s after reading %d bytes' % (destination_host, len(buf)))

        try:
            dest = create_connection((destination_host, self.port))
            dest.sendall(buf)
        except IOError, ex:
            self.logger.error('failed to connect to %s:%s: %s', destination_host, self.port, ex)
            return

        DuplexForwarder(source, dest, self.buffer_size, self.timeout).start()

    def buffer_until_host_known(self, source):
        buf = ''
        destination_host = None
        while destination_host is None:
            buf += source.recv(self.buffer_size)
            destination_host = self.parse_destination_host(buf)
        return destination_host, buf

    def parse_destination_host(self, data):
        raise NotImplementedError()


class HTTPProxy(BaseProxy):
    logger = logging.getLogger('HTTPProxy')
    port = 80

    def parse_destination_host(self, data):
        result = HOST_FROM_HTTP.search(data)
        return None if result is None else result.groups()[0]


class HTTPSProxy(BaseProxy):
    logger = logging.getLogger('HTTPSProxy')
    port = 443

    def parse_destination_host(self, data):
        return ClientHello(data).get_server_name()
