# -*- coding: utf-8 -*-

import urllib2
import struct
import random

import socket
import httplib
import urlparse
import ssl
from urllib2 import AbstractHTTPHandler, URLError, splittype, splithost, addinfourl
from email.generator import Generator
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_noop
from zope.interface import implementer
import logging
from io import BytesIO
from .interfaces import ISejNWTSUploader, ISejNWTSUploaderFactory

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

@implementer(ISejNWTSUploader)
class PythonNWTSUploader(object):
    def __init__(self, endpoint_url, terminal_id, password, cert_file=None, key_file=None, ca_certs=None):
        self.endpoint_url = endpoint_url
        self.terminal_id = terminal_id
        self.password = password
        self.cert_file = cert_file
        self.key_file = key_file
        self.ca_certs = ca_certs

    def __call__(self, application, file_id, data):
        url = urlparse.urljoin(self.endpoint_url, application)

        size = struct.pack('H', len(data))
        header = self.terminal_id + self.password + file_id + size + "\0\0\0\0\0\0"
        output = header + data
        mode = modes.get(file_id)
        thread_id = random.randint(1, 9999)

        req = urllib2.Request('%s?Mode=%d&ThreadID=%d' % (url, mode, thread_id))
        req._cert_reqs = ssl.CERT_REQUIRED
        req._cert_file = self.cert_file
        req._key_file = self.key_file
        req._ca_certs = self.ca_certs
        req.add_header('Connection', 'close')
        req.add_header('Cache-Control', 'no-cache')

        try:
            opener = build_opener()
            o = opener.open(req, output, socket._GLOBAL_DEFAULT_TIMEOUT)
            try:
                o.read()
            finally:
                o.close()
        except urllib2.HTTPError as e:
            if e.code == 800:
                # 800 は正常終了...
                pass
            else:
                raise

def build_multipart(params):
    m = MIMEMultipart('form-data')
    for k, (filename, data) in params.items():
        f = MIMEApplication(data, 'octet-stream', encode_noop)
        extra_params = {}
        if filename is not None:
            extra_params['filenanme'] = filename
        f.add_header('Content-Disposition', 'form-data', name=k, **extra_params)
        m.attach(f)
    fp = BytesIO()
    g = Generator(fp)
    g._dispatch(m)
    payload = fp.getvalue()
    if payload[-1] != '\n':
        payload += '\n'
    payload = payload.replace('\n', '\r\n')
    return payload, dict(p for p in m.items() if p[0].lower() != 'mime-version')

class MyPasswdMgr(urllib2.HTTPPasswordMgr):
    def find_user_password(self, realm, authuri):
        x = urllib2.HTTPPasswordMgr.find_user_password(self, realm, authuri)
        if x[0] is not None:
            return x
        return urllib2.HTTPPasswordMgr.find_user_password(self, None, authuri)

@implementer(ISejNWTSUploader)
class ProxyNWTSUploader(object):
    def __init__(self, proxy_url, proxy_auth_user, proxy_auth_password, endpoint_url, terminal_id, password):
        self.proxy_url = proxy_url
        self.proxy_auth_user = proxy_auth_user
        self.proxy_auth_password = proxy_auth_password
        self.endpoint = urlparse.urlparse(endpoint_url)
        self.terminal_id = terminal_id
        self.password = password
        auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr=MyPasswdMgr())
        if self.proxy_auth_user:
            auth_handler.add_password(realm=None, uri='/', user=self.proxy_auth_user, passwd=self.proxy_auth_password)
        self.auth_handler = auth_handler

    def __call__(self, application, file_id, data):
        opener = build_opener()
        opener.add_handler(self.auth_handler)
        data, headers = build_multipart({
                '-s': (None, self.endpoint.netloc),
                '-d': (None, self.endpoint.path),
                '-t': (None, self.terminal_id),
                '-p': (None, self.password),
                '-f': (None, file_id),
                '-e': (None, application),
                'zipfile': ('%s.zip' % file_id, data),
                })
        req = urllib2.Request(
            self.proxy_url,
            data=data,
            headers=headers
            )
        r = opener.open(req)
        try:
            if r.code == 200:
                logging.info('success')
            else:
                logging.error('proxy response = %s' % r.status)
        finally:
            r.close()


@implementer(ISejNWTSUploaderFactory)
class PythonNWTSUploaderFactory(object):
    def __init__(self, registry):
        ca_certs = settings.get('altair.sej.nwts.ca_certs')
        if ca_certs is None:
            logging.warning("altair.sej.nwts.ca_certs is not given. using deprecated sej.nwts.ca_certs instead")
            ca_certs = settings['sej.nwts.ca_certs']

        cert_file = settings.get('altair.sej.nwts.cert_file')
        if cert_file is None:
            logging.warning("altair.sej.nwts.cert_file is not given. using deprecated sej.nwts.cert_file instead")
            cert_file = settings['sej.nwts.cert_file']

        key_file = settings.get('altair.sej.nwts.key_file')
        if key_file is None:
            logging.warning("altair.sej.nwts.key_file is not given. using deprecated sej.nwts.key_file instead")
            key_file = settings['sej.nwts.key_file']

        self.ca_certs = ca_certs
        self.cert_file = cert_file
        self.key_file = key_file

    def __call__(self, endpoint_url, terminal_id, password):
        return PythonNWTSUploader(
            ca_certs=self.ca_certs,
            cert_file=self.cert_file,
            key_file=self.key_file,
            endpoint_url=endpoint_url,
            terminal_id=terminal_id,
            password=password
            )

@implementer(ISejNWTSUploaderFactory)
class ProxyNWTSUploaderFactory(object):
    def __init__(self, registry):
        settings = registry.settings
        proxy_url = settings.get('altair.sej.nwts.proxy_url')
        proxy_auth_user = settings.get('altair.sej.nwts.proxy_auth_user')
        if proxy_auth_user is None:
            logging.warning("altair.sej.nwts.proxy_auth_user is not given. using deprecated altair.sej.nwts.auth_user instead")
            proxy_auth_user = settings.get('altair.sej.nwts.auth_user')

        proxy_auth_password = settings.get('altair.sej.nwts.proxy_auth_password')
        if proxy_auth_password is None:
            logging.warning("altair.sej.nwts.proxy_auth_password is not given. using deprecated altair.sej.nwts.auth_pass instead")
            proxy_auth_password = settings.get('altair.sej.nwts.auth_pass')

        self.proxy_url = proxy_url
        self.proxy_auth_user = proxy_auth_user
        self.proxy_auth_password = proxy_auth_password

    def __call__(self, endpoint_url, terminal_id, password):
        return ProxyNWTSUploader(
            proxy_url=self.proxy_url,
            proxy_auth_user=self.proxy_auth_user,
            proxy_auth_password=self.proxy_auth_password,
            endpoint_url=endpoint_url,
            terminal_id=terminal_id,
            password=password
            )
        
