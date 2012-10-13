from twisted.internet import defer
from twisted.names import client, dns


class MappingResolver(client.Resolver):
    """
    A Resolver that maps a set of given domain to given ips and the rest will
    be forwarded to a real dns server
    """
    def __init__(self, mapping, servers):
        self.mapping = mapping
        self.ttl = 10
        client.Resolver.__init__(self, servers=servers)

    def lookupAddress(self, name, timeout=None):
        if name not in self.mapping:
            return client.Resolver.lookupAddress(self, name, timeout)

        d = defer.Deferred()
        d.callback([
            (dns.RRHeader(
                name, dns.A, dns.IN, self.ttl,
                dns.Record_A(self.mapping[name], self.ttl)),
            ), (), ()
        ])
        return d
