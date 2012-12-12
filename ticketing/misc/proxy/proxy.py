#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from urlparse import urlparse, urlunparse
import sys
import re
import os

SUBDOMAINS = [
    '89ers',
    'happinets',
    'tokyo-cr',
    ]

class MyProxyRequest(proxy.ProxyRequest):
    def rewrite(self, request_uri, headers):
        new_request_uri_str = request_uri_str = urlunparse(request_uri)
        for regexp, replace in self.channel.rewrite_patterns:
            new_request_uri_str = re.sub(regexp, replace, request_uri_str)
            if new_request_uri_str != request_uri_str:
                self.channel.factory.logFile.write("%s => %s\n" % (request_uri_str, new_request_uri_str))
                break
            request_uri_str = new_request_uri_str
        return urlparse(new_request_uri_str)

    def process(self):
        parsed = urlparse(self.uri)
        headers = self.getAllHeaders().copy()

        target = self.rewrite(parsed, headers)

        target_host = target.netloc
        target_port = self.ports[target.scheme]

        if ':' in target_host:
            # TODO: IPv6?
            target_host, target_port = target_host.split(':')
            target_port = int(target_port)

        rest = urlunparse(('http', '') + target[2:])[7:]
        if not rest:
            rest = rest + '/'

        class_ = self.protocols[target.scheme]
        if 'host' not in headers:
            headers['host'] = parsed.netloc

        self.content.seek(0, 0)
        s = self.content.read()
        clientFactory = class_(self.method, rest, self.clientproto, headers,
                               s, self)
        self.reactor.connectTCP(target_host, target_port, clientFactory)

class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest
    rewrite_patterns = [
        (r'http://backend.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:7654\1'),
        (r'http://cms.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:6543\1'),
        (r'http://stg2.rt.ticketstar.jp(/89ers/booster(?:/.*)?)', r'http://localhost:7657\1'),
        (r'http://stg2.rt.ticketstar.jp(/mypage(?:/.*)?)', r'http://localhost:7656\1'),
        ]

    def __init__(self, *args, **kwargs):
        proxy.Proxy.__init__(self, *args, **kwargs)
        self.rewrite_patterns = list(self.rewrite_patterns)
        for subdomain in SUBDOMAINS:
            self.rewrite_patterns.extend([
                (r'http://%s.stg2.rt.ticketstar.jp(/orderreview(?:/.*)?)' % subdomain, r'http://localhost:7659\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/lots(?:/.*)?)' % subdomain, r'http://localhost:7657\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/cart(?:/.*)?)' % subdomain, r'http://localhost:7655\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/.*)?' % subdomain, r'http://localhost:5432\1'),
                ])

class ProxyFactory(http.HTTPFactory):
    protocol = MyProxy

if __name__ == '__main__':
    tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    log.startLogging(open(os.path.join(tmpdir, 'access.log'), 'w'))
    reactor.listenTCP(58080, ProxyFactory())
    reactor.run()
