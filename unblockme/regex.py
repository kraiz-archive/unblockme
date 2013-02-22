import re


_domain = '[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})*'

_from_domain = lambda d: re.sub(r'^\\.', '(.+\.)?', d.replace('.', '\.'))

HOST_FROM_HTTP = re.compile(r'Host:\s+(%s)' % _domain)

FROM_DOMAIN = lambda d: re.compile(_from_domain(d))

FROM_DOMAINS = lambda ds: re.compile('(%s)' % '|'.join(map(_from_domain, ds)))
