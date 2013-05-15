# -*- coding: utf-8 -*-

import urllib2
import struct
import random

import socket
import httplib
import ssl
from urllib2 import AbstractHTTPHandler, URLError, splittype, splithost, addinfourl

import logging

logger = logging.getLogger(__name__)

class OurHTTPSConnection(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        ca_certs = kwargs.pop('ca_certs', None)
        cert_reqs = kwargs.pop('cert_reqs', None)
        if cert_reqs is None:
            cert_reqs = ssl.CERT_NONE
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)
        self.ca_certs = ca_certs
        self.cert_reqs = cert_reqs

    def connect(self):
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        logger.debug('cert_file=%s, key_file=%s, cert_reqs=%d, ca_certs=%s' % (self.cert_file, self.key_file, self.cert_reqs, self.ca_certs))
        self.sock = ssl.wrap_socket(
            sock,
            keyfile=self.key_file,
            certfile=self.cert_file,
            cert_reqs=self.cert_reqs,
            ca_certs=self.ca_certs
            )

class SejHTTPHandler(AbstractHTTPHandler):
    def do_request_(self, request):
        host = request.get_host()
        if not host:
            raise URLError('no host given')

        if request.has_data():  # POST
            data = request.get_data()
            if not request.has_header('Content-length'):
                request.add_unredirected_header(
                    'Content-length', '%d' % len(data))

        sel_host = host
        if request.has_proxy():
            scheme, sel = splittype(request.get_selector())
            sel_host, sel_path = splithost(sel)

        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)

        return request

    http_request = do_request_
    https_request = do_request_

    def http_open(self, req):
        return self.do_open(httplib.HTTPConnection, req)

    def https_open(self, req):
        def https_connection_factory(host, **kwargs):
            return OurHTTPSConnection(
                host,
                cert_reqs=req._cert_reqs if hasattr(req, '_cert_reqs') else None,
                cert_file=req._cert_file if hasattr(req, '_cert_file') else None,
                key_file=req._key_file if hasattr(req, '_key_file') else None,
                ca_certs=req._ca_certs if hasattr(req, '_ca_certs') else None,
                **kwargs
                )
        return self.do_open(https_connection_factory, req)

    def do_open(self, http_class, req):
        host = req.get_host()
        if not host:
            raise URLError('no host given')

        h = http_class(host, timeout=req.timeout) # will parse host:port
        h.set_debuglevel(self._debuglevel)

        headers = dict(req.unredirected_hdrs)
        headers.update(dict((k, v) for k, v in req.headers.items()
                            if k not in headers))

        headers["Connection"] = "close"
        headers = dict(
            (name.title(), val) for name, val in headers.items())

        if req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = "Proxy-Authorization"
            if proxy_auth_hdr in headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                # Proxy-Authorization should not be sent to origin
                # server.
                del headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)

        try:
            h.request(req.get_method(), req.get_selector(), req.data, headers)
            try:
                r = h.getresponse(buffering=True)
            except TypeError: #buffering kw not supported
                r = h.getresponse()
        except socket.error, err: # XXX what error?
            raise URLError(err)

        r.recv = r.read
        fp = socket._fileobject(r, close=True)

        resp = addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        return resp

modes = dict(
    SEIT020U = 1,
    SDMT010U = 2,
    TEST010U = 1,
)

def build_opener():
    opener = urllib2.OpenerDirector()
    opener.add_handler(urllib2.ProxyHandler())
    opener.add_handler(urllib2.UnknownHandler())
    opener.add_handler(SejHTTPHandler())
    opener.add_handler(urllib2.HTTPDefaultErrorHandler())
    opener.add_handler(urllib2.HTTPRedirectHandler())
    opener.add_handler(urllib2.HTTPErrorProcessor())
    return opener

def nws_data_send(url, terminal_id, password, file_id, data, cert_file=None, key_file=None, ca_certs=None):

    size=struct.pack('H', len(data))
    header = terminal_id+password+file_id+size+"\0\0\0\0\0\0"
    output = header+data
    mode = modes.get(file_id)
    thread_id = random.randint(1, 9999)

    req = urllib2.Request('%s?Mode=%d&ThreadID=%d' % (url, mode, thread_id))
    req._cert_reqs = ssl.CERT_REQUIRED
    req._cert_file = cert_file
    req._key_file = key_file
    req._ca_certs = ca_certs
    req.add_header('Connection', 'close')
    req.add_header('Cache-Control', 'no-cache')

    try:
        opener = build_opener()
        opener.open(req, output, socket._GLOBAL_DEFAULT_TIMEOUT)

    except urllib2.HTTPError as e:
        if e.code == 800:
            return True
        raise e
