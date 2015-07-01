from ftplib import FTP_TLS
import socket
import ssl

class FTP_TLS_(object, FTP_TLS):
    def __init__(self, host='', user='', passwd='', acct='', keyfile=None, certfile=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, ca_certs=None, implicit=False):
        self.ca_certs = ca_certs
        self.implicit = implicit
        FTP_TLS.__init__(self, host, user, passwd, acct, keyfile, certfile, timeout)

    def connect(self, host='', port=0, timeout=-999):
        if host != '':
            self.host = host
        if port > 0:
            self.port = port
        if timeout != -999:
            self.timeout = timeout
        self.sock = socket.create_connection((self.host, self.port), self.timeout)
        self.af = self.sock.family
        if self.implicit:
            self._wrap_socket()
        else:
            self.file = self.sock.makefile('rb')
        self.welcome = self.getresp()
        return self.welcome

    def _wrap_socket(self):
        self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile,
                                    ssl_version=self.ssl_version, ca_certs=self.ca_certs)
        self.file = self.sock.makefile(mode='rb')

    def auth(self):
        '''Set up secure control connection by using TLS/SSL.'''
        if not self.implicit:
            if isinstance(self.sock, ssl.SSLSocket):
                raise ValueError("Already using TLS")
            if self.ssl_version == ssl.PROTOCOL_TLSv1:
                resp = self.voidcmd('AUTH TLS')
            else:
                resp = self.voidcmd('AUTH SSL')
            self._wrap_socket()
            return resp
