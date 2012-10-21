from twisted.names import dns


class AuthedDNSDatagramProtocol(dns.DNSDatagramProtocol):

    def __init__(self, controller, validator, reactor=None):
        super(AuthedDNSDatagramProtocol, self).__init__(controller,
                                                        reactor=reactor)
        self.validator = validator

    def datagramReceived(self, data, addr):
        if self.validator.valid_client(addr[0], 'dns'):
            return dns.DNSDatagramProtocol.datagramReceived(self, data, addr)
        else:
            self.transport.loseConnection()
