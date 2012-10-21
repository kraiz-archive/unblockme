import re, sys
from bottle import Bottle, request, run


if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    CLIENTS_FILE = 'allowed.clients.acl'
    DOMAINS_FILE = 'allowed.domains.acl'
    IP_HEADER = 'REMOTE_ADDR'
    HOST = '127.0.0.1'
    AUTORELOAD = True
else:
    CLIENTS_FILE = '/etc/squid3/allowed.clients.acl'
    DOMAINS_FILE = '/etc/squid3/allowed.domains.acl'
    IP_HEADER = 'HTTP_X_FORWARDED_FOR'
    HOST = '127.0.0.2'
    AUTORELOAD = False


app = Bottle()

def read_lines_from_file(filename):
    for line in open(filename):
        yield line.strip()

def is_valid_client(ip):
    return ip in list(read_lines_from_file(CLIENTS_FILE))

@app.route('/proxy.pac')
def index():
    fix = ''
    if is_valid_client(request.environ[IP_HEADER]):
        fix = '\n'.join([
            'if (shExpMatch(host,"%s")) { return "PROXY 199.195.251.154:3128"; }' %
            re.sub(r'^(\.)', '*.', domain)
            for domain in read_lines_from_file(DOMAINS_FILE)
        ])
    return 'function FindProxyForURL(url, host){' + fix + 'return "DIRECT";}'

run(app, host=HOST, port='3000', reloader=AUTORELOAD)
