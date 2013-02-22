from gevent import monkey

monkey.patch_all()

import gevent
import argparse
import ConfigParser
import logging

from unblockme.dns import DNSServer
from unblockme.proxy import HTTPProxy, HTTPSProxy


def main():
    # parse cli params
    parser = argparse.ArgumentParser(description='Frabble the foo and the bars')
    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='debug mode, logging to stdout, default: /var/log/unblockme.log')
    parser.add_argument(
        '-c', '--config', dest='config', default='/etc/unblockme.conf', metavar='FILE',
        help='the config file to read from, default: /etc/unblockme.conf')
    args = parser.parse_args()

    # setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARN,
        format='%(asctime)s %(levelname)-8s %(message)s',
        filename=None if args.debug else '/var/log/unblockme.log'
    )

    # parse config & log
    cfg = ConfigParser.ConfigParser()
    logging.info('Reading config form %s' % args.config)
    cfg.read(args.config)

    interface = cfg.get('unblockme', 'bind-address')
    logging.info('Starting unblockme at %s' % interface)

    clients = [s.strip() for s in cfg.get('unblockme', 'clients').split(',')]
    logging.info('clients: %s' % ', '.join(clients))

    domains = [s.strip() for s in cfg.get('unblockme', 'domains').split(',')]
    logging.info('domains: %s' % ', '.join(domains))

    # start services
    http = HTTPProxy('%s:80' % interface)
    https = HTTPSProxy('%s:443' % interface)
    dns = DNSServer('%s:53' % interface, proxy_ip=interface, mapped_domains=domains)

    try:
        http.start()
        https.start()
        dns.start()
        gevent.wait()
    except Exception as e:
        logging.error(e)
        exit(1)
    finally:
        dns.stop()
        https.stop()
        http.stop()


def kill_zombies():
    """kills some old processes, that maybe block ports"""
    import os, psutil
    me = psutil.Process(os.getpid())
    for p in psutil.process_iter():
        if p.cmdline == me.cmdline and me.pid != p.pid:
            p.kill()

if __name__ == "__main__":
    kill_zombies()


    import cProfile

    cProfile.run("main()")


