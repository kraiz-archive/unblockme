from twisted.internet import defer, protocol
from twisted.python import log


class TCPProxyServerProtocol(protocol.Protocol):

    def connectionMade(self):
        self.srv_queue = defer.DeferredQueue()
        self.cli_queue = defer.DeferredQueue()
        self.srv_queue.get().addCallback(self.clientDataReceived)

#        factory = ProxyClientFactory(self.srv_queue, self.cli_queue)
#        reactor.connectTCP("127.0.0.1", 6666, factory)

    def clientDataReceived(self, chunk):
        log.msg('ProxyServer: received %d bytes from target server' % len(chunk))
        self.transport.write(chunk)
        self.srv_queue.get().addCallback(self.clientDataReceived)

    def dataReceived(self, chunk):
        log.msg('ProxyServer: %d bytes received from client' % len(chunk))
        self.cli_queue.put(chunk)

        r'\s((\w\.)\w+\.\w+)\s'

    def connectionLost(self, why):
        self.cli_queue.put(False)


class TCPProxyServerFactory(protocol.Factory):
    protocol = TCPProxyServerProtocol
