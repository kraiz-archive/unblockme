import logging

from twisted.internet import defer
from twisted.names import client, dns

from unblockme.regex import FROM_DOMAIN


class MappingResolver(client.Resolver):

    def __init__(self, mapping, servers):
        self.mapping = dict((FROM_DOMAIN(domain), ip)
                            for domain, ip in mapping.iteritems())
        self.ttl = 1
        client.Resolver.__init__(self, servers=servers)

    def lookupAddress(self, name, timeout=None):
        for domain, ip in self.mapping.iteritems():
            if domain.match(name) is not None:
                logging.debug('lookupAddress matched %s' % name)
                d = defer.Deferred()
                d.callback([
                    (dns.RRHeader(name, dns.A, dns.IN, self.ttl,
                                  dns.Record_A(ip, self.ttl)),),
                    (), ()
                ])
                return d
        return client.Resolver.lookupAddress(self, name, timeout)
