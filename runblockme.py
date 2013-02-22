#!python
print "test"
from gevent import monkey

monkey.patch_all()

import ConfigParser
import logging
import sys

from unblockme.dns import DNSServer
from unblockme.proxy import HTTPProxy, HTTPSProxy


if __name__ == "__main__":
    # REPL/DEBUG flag
    DEBUG = sys.argv[1] == 'debug'

    print "test"

    # logging
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.WARN,
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename=None if DEBUG else '/var/log/unblockme.log'
    )

    # parse config & log
    cfg = ConfigParser.ConfigParser()
    cfg.read('unblockme/deploy/unblockme.conf' if DEBUG else '/etc/unblockme.conf')

    interface = cfg.get('unblockme', 'bind-address')
    logging.info('Starting unblockme at %s' % interface)

    clients = [s.strip() for s in cfg.get('unblockme', 'clients').split(',')]
    logging.info('clients: %s' % ', '.join(clients))

    domains = [s.strip() for s in cfg.get('unblockme', 'domains').split(',')]
    logging.info('domains: %s' % ', '.join(domains))

    # start services
    http = HTTPProxy('%s:1080' % interface)
    https = HTTPSProxy('%s:1443' % interface)
    dns = DNSServer('%s:1053' % interface, proxy_ip=interface, mapped_domains=domains)

    http.start()
    https.start()
    dns.serve_forever()
    https.stop()
    http.stop()
