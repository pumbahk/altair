# -*- coding: utf-8 -*-

import logging
import urllib2
import struct
import random
import socket
import httplib
import urlparse
import ssl
from io import BytesIO
from urllib2 import AbstractHTTPHandler, URLError, splittype, splithost, addinfourl
from email.generator import Generator
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.encoders import encode_noop
from zope.interface import implementer
from altair.app.ticketing.urllib2ext import build_opener
from altair.httphelpers.httplib import OurHTTPSConnection
from .interfaces import ISejNWTSUploader, ISejNWTSUploaderFactory

logger = logging.getLogger(__name__)


modes = dict(
    SEIT020U = 1,
    SDMT010U = 2,
    TEST010U = 1,
)


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
        req.add_unredirected_header('Content-type', None)

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
            auth_handler.add_password(realm=None, uri=proxy_url, user=self.proxy_auth_user, passwd=self.proxy_auth_password)
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
        
