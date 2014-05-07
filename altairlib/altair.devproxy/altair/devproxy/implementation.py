# -*- coding:utf-8 -*-
from twisted.web import proxy, http
from twisted.internet import protocol
from urlparse import urlparse, urlunparse
import re

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

