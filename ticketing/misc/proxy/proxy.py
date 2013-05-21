#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.internet import protocol
from urlparse import urlparse, urlunparse
import sys
import re
import os

SUBDOMAINS = [
    '89ers',
    'happinets',
    'tokyo-cr',
    'vissel',
    'c',
    'rt',
    ]

class ProxyConnectClientDecoder(object):
    def __init__(self, client):
        self.client = client

    def dataReceived(self, data):
        self.client.transport.write(data)

class ProxyConnectClient(protocol.Protocol):
    def setFather(self, father):
        self.father = father
        self.father.channel._transferDecoder = ProxyConnectClientDecoder(self)
        self.father.channel.setRawMode()

    def connectionMade(self):
        self.father.setResponseCode(200, 'Connection established')
        self.father.write('')
        self.father.transport.resumeProducing()

    def dataReceived(self, data):
        self.father.transport.write(data)

class ProxyConnectClientFactory(protocol.ClientFactory):
    protocol = ProxyConnectClient

    def __init__(self, command, rest, version, headers, data, father):
        self.father = father
        self.command = command
        self.rest = rest
        self.headers = headers
        self.data = data

    def buildProtocol(self, *args, **kwargs):
        prot = protocol.ClientFactory.buildProtocol(self, *args, **kwargs)
        prot.setFather(self.father)
        return prot

    def clientConnectionFailed(self, connector, reason):
        self.father.finish()

class MyProxyRequest(proxy.ProxyRequest):
    ports = dict(https=443, **proxy.ProxyRequest.ports)

    def rewrite(self):
        if self.method == 'CONNECT':
            self.target_host, port = self.uri.split(':')
            self.target_port = int(port)
            self.target_parsed = None
        else:
            new_request_uri_str = request_uri_str = self.uri
            for regexp, replace in self.channel.rewrite_patterns:
                new_request_uri_str = re.sub(regexp, replace, request_uri_str)
                if new_request_uri_str != request_uri_str:
                    self.channel.factory.logFile.write("%s => %s\n" % (request_uri_str, new_request_uri_str))
                    break
                request_uri_str = new_request_uri_str
            self.target_uri = new_request_uri_str
            self.target_parsed = urlparse(new_request_uri_str)
            if ':' in self.target_parsed.netloc:
                # TODO: IPv6?
                self.target_host, port = self.target_parsed.netloc.split(':')
                self.target_port = int(port)
            else:
                self.target_host = self.target_parsed.netloc
                self.target_port = self.ports[self.target_parsed.scheme]

    def get_connector_class(self):
        if self.method == 'CONNECT':
            return ProxyConnectClientFactory
        else:
            return proxy.ProxyClientFactory

    def process(self):
        self.parsed = urlparse(self.uri)
        self.target_headers = self.getAllHeaders().copy()
        self.rewrite()

        rest = None
        if self.target_parsed is not None:
            rest = urlunparse(('http', '') + self.target_parsed[2:])[7:]
            if not rest:
                rest = rest + '/'

        class_ = self.get_connector_class()
        if 'host' not in self.target_headers:
            self.target_headers['host'] = self.parsed.netloc

        self.content.seek(0, 0)
        s = self.content.read()
        client = class_(self.method, rest, self.clientproto, self.target_headers, s, self)
        self.reactor.connectTCP(self.target_host, self.target_port, client)

class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest
    rewrite_patterns = [
        (r'http://backend.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:7654\1'),
        (r'http://cms.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:6543\1'),
        (r'http://stg2.rt.ticketstar.jp(/89ers/booster(?:/.*)?)', r'http://localhost:7657\1'),
        (r'http://89ers.stg2.rt.ticketstar.jp(/89ers/booster(?:/.*)?)', r'http://localhost:7657\1'),
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
                (r'http://%s.stg2.rt.ticketstar.jp(/maintenance(?:/.*)?)' % subdomain, r'http://localhost:8000\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/.*)?' % subdomain, r'http://localhost:5432\1'),
                ])

class ProxyFactory(http.HTTPFactory):
    protocol = MyProxy

if __name__ == '__main__':
    tmpdir = os.path.join(os.path.dirname(__file__), 'tmp')
    port = 58080
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    sys.stderr.write("proxy port:%d\n" % port)
    log.startLogging(open(os.path.join(tmpdir, 'access.log'), 'w'))
    reactor.listenTCP(port, ProxyFactory())
    reactor.run()
