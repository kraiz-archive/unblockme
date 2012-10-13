from twisted.application import internet, service
from twisted.names import dns, server, cache

from unblockme import proxy, resolver


# dns instanciation
dns_resolver = resolver.MappingResolver(mapping={'kraiz.com': '127.0.0.1'},
                                        servers=[('8.8.8.8', 53)])
dns_factory = server.DNSServerFactory(clients=[dns_resolver],
                                      caches=[cache.CacheResolver()])
dns_protocol = dns.DNSDatagramProtocol(controller=dns_factory)

# tcp proxy instanciation
proxy_factory = proxy.TCPProxyServerFactory()

# stack anything together
application = service.Application('unblockme', uid=1, gid=1)
serviceCollection = service.IServiceCollection(application)
internet.UDPServer(53, dns_protocol).setServiceParent(serviceCollection)
internet.TCPServer(443, proxy_factory).setServiceParent(serviceCollection)
