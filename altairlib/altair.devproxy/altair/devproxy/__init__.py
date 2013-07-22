#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log
from twisted.internet import protocol
from urlparse import urlparse, urlunparse
import sys
import re
import os
import argparse

SUBDOMAINS = [
    '89ers',
    'happinets',
    'tokyo-cr',
    'vissel',
    'c',
    'rt',
    'bambitious',
    'bigbulls',
    'lakestars',
    'kings',
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
        self.override_host = None
        if self.method == 'CONNECT':
            self.target_host, port = self.uri.split(':')
            self.target_port = int(port)
            self.target_parsed = None
        else:
            new_request_uri_str = self.uri

            for regexp, replace in self.channel.prerewrite_patterns:
                new_request_uri_str = re.sub(regexp, replace, new_request_uri_str)

            if new_request_uri_str != self.uri:
                self.channel.factory.logFile.write("[prerewrite] %s => %s\n" % (self.uri, new_request_uri_str))
                self.uri = new_request_uri_str
                self.override_host = urlparse(self.uri).netloc

            new_request_uri_str = self.uri
            for regexp, replace in self.channel.rewrite_patterns:
                new_request_uri_str = re.sub(regexp, replace, new_request_uri_str)
            if new_request_uri_str != self.uri:
                self.channel.factory.logFile.write("[rewrite] %s => %s\n" % (self.uri, new_request_uri_str))

            self.target_uri = new_request_uri_str
            self.target_parsed = urlparse(new_request_uri_str)
            if ':' in self.target_parsed.netloc:
                # TODO: IPv6?
                self.target_host, port = self.target_parsed.netloc.split(':')
                self.target_port = int(port)
            else:
                self.target_host = self.target_parsed.netloc
                self.target_port = self.ports.get(self.target_parsed.scheme)

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
        if self.override_host:
            self.target_headers['host'] = self.override_host
        if 'host' not in self.target_headers:
            self.target_headers['host'] = self.parsed.netloc

        self.content.seek(0, 0)
        s = self.content.read()
        if self.target_port is None:
            self.setResponseCode(http.BAD_REQUEST)
            self.finish()
        else:
            client = class_(self.method, rest, self.clientproto, self.target_headers, s, self)
            self.reactor.connectTCP(self.target_host, self.target_port, client)

class MyProxy(proxy.Proxy):
    requestFactory = MyProxyRequest
    prerewrite_patterns = [
        (r'http://api.ticket.rakuten.co.jp/rid/rc/http/stg/([^/]+)(/.+)?/(verify.*)', r'http://\1.stg2.rt.ticketstar.jp\2/\3'),
        ]

    rewrite_patterns = [
        (r'http://backend.stg2.rt.ticketstar.jp(/qrreader(?:/.*)?)', r'http://localhost:8030\1'),
        (r'http://backend.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:8021\1'),
        (r'http://cms.stg2.rt.ticketstar.jp(/.*)?', r'http://localhost:8001\1'),
        (r'http://89ers.stg2.rt.ticketstar.jp(/booster(?:/.*)?)', r'http://localhost:9081\1'),
        (r'http://bambitious.stg2.rt.ticketstar.jp(/booster(?:/.*)?)', r'http://localhost:9082\1'),
        (r'http://bigbulls.stg2.rt.ticketstar.jp(/booster(?:/.*)?)', r'http://localhost:9083\1'),
        ]

    def __init__(self, *args, **kwargs):
        proxy.Proxy.__init__(self, *args, **kwargs)
        self.prerewrite_patterns = list(self.prerewrite_patterns)
        self.rewrite_patterns = list(self.rewrite_patterns)
        for subdomain in SUBDOMAINS:
            self.rewrite_patterns.extend([
                (r'http://%s.stg2.rt.ticketstar.jp(/orderreview(?:/.*)?)' % subdomain, r'http://localhost:9061\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/lots(?:/.*)?)' % subdomain, r'http://localhost:9121\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/cart(?:/.*)?)' % subdomain, r'http://localhost:9021\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/whattime(?:/.*)?)' % subdomain, r'http://localhost:9071\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/maintenance(?:/.*)?)' % subdomain, r'http://localhost:8000\1'),
                (r'http://%s.stg2.rt.ticketstar.jp(/.*)?' % subdomain, r'http://localhost:9001\1'),
                ])

class ProxyFactory(http.HTTPFactory):
    protocol = MyProxy

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--log', dest='log', type=str, nargs=1,
                        help='access log')
    parser.add_argument('address', type=str, nargs=1,
                        help='the server address to listen on')
    args = parser.parse_args()

    addr_or_port, semi, port = args.address[0].partition(':')
    if not semi:
        addr = None
        port = int(addr_or_port)
    else:
        addr = addr_or_port
        port = int(port)
    if not addr:
        addr = ''

    sys.stderr.write("Listening on %s:%d\n" % (addr, port))
    if args.log:
        out = open(args.log[0], 'a')
    else:
        out = sys.stderr
    log.startLogging(out)
    reactor.listenTCP(port, ProxyFactory(), 10, addr)
    reactor.run()

if __name__ == '__main__':
    main()
