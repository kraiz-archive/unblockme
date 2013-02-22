import unittest

from gevent import subprocess

from unblockme.dns import DNSServer

from socket import gethostbyname


class DNSTestCase(unittest.TestCase):
    def setUp(self):
        self.dns = DNSServer(':5353',
            proxy_ip='10.0.0.1',
            mapped_domains=['.netflix.com', 'grooveshark.com']
        )
        self.dns.start()

    def tearDown(self):
        """Kill the running dns server"""
        self.dns.stop()

    def dig_local(self, domain):
        """Helper requesting the running dns server for an ip for the given domain"""
        return subprocess.check_output(
            'dig @localhost -p 5353 +short %s' % domain,
            shell=True, stderr=subprocess.STDOUT
        ).strip()

    def test_resolve_forwarded(self):
        self.assertEqual(self.dig_local('kraiz.de'), gethostbyname('kraiz.de'))

    def test_resolve_single_mapped(self):
        self.assertEqual(self.dig_local('grooveshark.com'), '10.0.0.1')

    def test_resolve_single_mapped_subdomain(self):
        self.assertEqual(self.dig_local('stream2.grooveshark.com'), gethostbyname('stream2.grooveshark.com'))

    def test_resolve_recursive_mapped(self):
        self.assertEqual(self.dig_local('netflix.com'), '10.0.0.1')

    def test_resolve_recursive_mapped_subdomain(self):
        self.assertEqual(self.dig_local('movies.netflix.com'), '10.0.0.1')

    def test_resolve_recursive_mapped_subsubdomain(self):
        self.assertEqual(self.dig_local('lala.news.netflix.com'), '10.0.0.1')

    def test_reverse_lookup_in_local_network(self):
        self.assertEqual(self.dig_local('113.1.168.192.in-addr.arpa'), ';; Warning: query response not set')

    def test_invalid_domain(self):
        self.assertEqual(self.dig_local('fg35otr4r.d4.fr34t4'), ';; Warning: query response not set')

if __name__ == '__main__':
    unittest.main()
