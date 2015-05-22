from ftplib import FTP_TLS
from socket import _GLOBAL_DEFAULT_TIMEOUT
import ssl

class FTP_TLS_(FTP_TLS):
    def __init__(self, host='', user='', passwd='', acct='', keyfile=None, certfile=None, timeout=_GLOBAL_DEFAULT_TIMEOUT, ca_certs=None):
        FTP_TLS.__init__(self, host, user, passwd, acct, keyfile, certfile, timeout)
        self.ca_certs = ca_certs

    def auth(self):
        '''Set up secure control connection by using TLS/SSL.'''
        if isinstance(self.sock, ssl.SSLSocket):
            raise ValueError("Already using TLS")
        if self.ssl_version == ssl.PROTOCOL_TLSv1:
            resp = self.voidcmd('AUTH TLS')
        else:
            resp = self.voidcmd('AUTH SSL')
        self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile,
                                    ssl_version=self.ssl_version, ca_certs=self.ca_certs)
        self.file = self.sock.makefile(mode='rb')
        return resp
