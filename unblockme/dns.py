import logging

from dnslib import DNSRecord
from gevent.server import DatagramServer
from socket import gethostbyname, gaierror

from unblockme.regex import FROM_DOMAIN


class DNSServer(DatagramServer):
    """
    Simple DNS server mapping all given 'mapped_domains' to 'proxy_ip' and forwards all other using systems dns server.
    """

    def __init__(self, *args, **kwargs):
        self.proxy_ip = kwargs.pop('proxy_ip')
        self.proxy_ip_reversed = '.'.join(reversed(self.proxy_ip.split('.')))
        self.mapped_domains_regexed = [FROM_DOMAIN(domain) for domain in kwargs.pop('mapped_domains')]
        self.mapped_domain_cache = set()
        self.logger = logging.getLogger('unblockme.dns.DNSServer')
        DatagramServer.__init__(self, *args, **kwargs)

    def handle(self, data, address):
        # parse udp datagram as dns request record
        try:
            request = DNSRecord.parse(data)
        except:
            # no real dns request, so simple close connection
            self.socket.close()
        else:
            # extract domain from dns request
            domain = str(request.get_q().get_qname())

            self.logger.debug('%s requested domain: %s' % (address, domain))

            # if that is the dns server name check
            if domain.startswith(self.proxy_ip_reversed):
                self.socket.sendto(request.reply(data="deiner Mutter").pack(), address)
                return

            # decide if mapped or not
            if self.is_mapped(domain):
                response = self.handle_mapped(domain, request)
            else:
                response = self.handle_forwarded(domain, request)

            # answer
            self.socket.sendto(response.pack(), address)

    def is_mapped(self, domain):
        """Checks wether the requested domain is a mapped one or not"""
        # check for cache hit
        if domain in self.mapped_domain_cache:
            return True
        # do the long run with regex testing
        for domain_regex in self.mapped_domains_regexed:
            if domain_regex.match(domain):
                self.mapped_domain_cache.add(domain)
                return True
            # none of the mapped domains
        return False

    def handle_mapped(self, domain, request):
        return request.reply(data=self.proxy_ip)

    def handle_forwarded(self, domain, request):
        try:
            return request.reply(data=gethostbyname(domain))
        except gaierror:
            # can't be resolved
            request.header.rcode = 3
            return request
