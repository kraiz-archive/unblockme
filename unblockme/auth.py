import logging

from twisted.internet import reactor
from twisted.names import client

from unblockme.regex import FROM_DOMAINS


class Validator(object):

    def __init__(self, clients, domains, client_refresh=5):
        self.client_dns_ip_mapping = dict((d, None) for d in clients)
        self.client_refresh = client_refresh * 60
        self.domains_re = FROM_DOMAINS(domains)
        reactor.callLater(0, self.refresh_mapping)

    def refresh_mapping(self):
        for dns in self.client_dns_ip_mapping.keys():
            client.getHostByName(dns).addCallback(
                self.client_mapping_refreshed,
                dns
            )
        reactor.callLater(self.client_refresh, self.refresh_mapping)

    def client_mapping_refreshed(self, ip, dns):
        self.client_dns_ip_mapping[dns] = ip

    def valid_client(self, client, proto):
        result = client in self.client_dns_ip_mapping.values()
        if not result:
            logging.warn('Unauthorized request (%s) from %s' % (proto, client))
        return result

    def valid_domain(self, client, proto, domain):
        result = self.domains_re.match(domain) is not None
        if not result:
            logging.warn('Unauthorized request (%s) from %s to %s' % (
                proto, client, domain)
            )
        return result
