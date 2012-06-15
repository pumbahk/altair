# -*- coding: utf-8 -*-

from urllib2 import Request, HTTPError, urlopen, build_opener
import struct

import socket
from urllib2 import HTTPSHandler, HTTPHandler, URLError, splittype, splithost, addinfourl
import httplib

key_file=None
cert_file=None
class SejHTTPHandler(HTTPHandler):

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

class SejHTTPSWithCertHandler(SejHTTPHandler):

    https_request = SejHTTPSWithCertHandler.do_request_

    def do_open(self, http_class, req):
        host = req.get_host()
        if not host:
            raise URLError('no host given')

        h = http_class(host, timeout=req.timeout, key_file=key_file, cert_file=cert_file) # will parse host:port
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
    SDMT010U = 2
)

def nws_data_send(url, terminal_id, password, file_id, data):

    size=struct.pack('H', len(data))
    header = terminal_id+password+file_id+size+"\0\0\0\0\0\0"
    output = header+data
    mode = modes.get(file_id)

    req = Request('%s?Mode=%d&ThreadID=9' % (url, mode))
    req.add_header('Connection', 'close')

    try:
        opener = build_opener(SejHTTPHandler, SejHTTPSWithCertHandler)
        opener.open(req, output, socket._GLOBAL_DEFAULT_TIMEOUT)

    except HTTPError, e:
        if e.code == 800:

            return True
        print e.read()
        raise e

