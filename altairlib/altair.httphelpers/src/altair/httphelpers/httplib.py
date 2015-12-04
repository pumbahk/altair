from __future__ import absolute_import

import ssl
import socket
import httplib

import logging

logger = logging.getLogger(__name__)

class OurHTTPSConnection(httplib.HTTPSConnection):
    def __init__(self, *args, **kwargs):
        ca_certs = kwargs.pop('ca_certs', None)
        cert_reqs = kwargs.pop('cert_reqs', None)
        if cert_reqs is None:
            cert_reqs = ssl.CERT_NONE
        ssl_version = kwargs.pop('ssl_version', ssl.PROTOCOL_SSLv23)
        httplib.HTTPSConnection.__init__(self, *args, **kwargs)
        self.ca_certs = ca_certs
        self.cert_reqs = cert_reqs
        self.ssl_version = ssl_version or ssl.PROTOCOL_SSLv23

    def connect(self):
        logger.debug('key_file=%s, cert_file=%s, cert_reqs=%d, ca_certs=%s, ssl_version=%d' % (self.key_file, self.cert_file, self.cert_reqs, self.ca_certs, self.ssl_version))
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(
            sock,
            keyfile=self.key_file,
            certfile=self.cert_file,
            cert_reqs=self.cert_reqs,
            ca_certs=self.ca_certs,
            ssl_version=self.ssl_version
            )
        logger.debug('cipher=%r' % (self.sock.cipher(), ))
