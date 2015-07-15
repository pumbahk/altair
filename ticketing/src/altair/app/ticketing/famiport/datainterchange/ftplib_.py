from ftplib import FTP_TLS, FTP
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

    def ntransfercmd(self, cmd, rest=None):
        conn, size = FTP.ntransfercmd(self, cmd, rest)
        if self.implicit or self._prot_p:
            conn = ssl.wrap_socket(conn, self.keyfile, self.certfile,
                                   ssl_version=self.ssl_version,
								   ca_certs=self.ca_certs)
        return conn, size

    def retrbinary(self, cmd, callback, blocksize=8192, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        try:
            while 1:
                data = conn.recv(blocksize)
                if not data:
                    break
                callback(data)
            # shutdown ssl layer
            if not self.implicit and isinstance(conn, ssl.SSLSocket):
                conn = conn.unwrap()
        finally:
            conn.close()
        return self.voidresp()

    def retrlines(self, cmd, callback = None):
        if callback is None: callback = print_line
        resp = self.sendcmd('TYPE A')
        conn = self.transfercmd(cmd)
        fp = conn.makefile('rb')
        try:
            while 1:
                line = fp.readline(self.maxline + 1)
                if len(line) > self.maxline:
                    raise Error("got more than %d bytes" % self.maxline)
                if self.debugging > 2: print '*retr*', repr(line)
                if not line:
                    break
                if line[-2:] == CRLF:
                    line = line[:-2]
                elif line[-1:] == '\n':
                    line = line[:-1]
                callback(line)
            # shutdown ssl layer
            if not self.implicit and isinstance(conn, ssl.SSLSocket):
                conn = conn.unwrap()
        finally:
            fp.close()
            conn.close()
        return self.voidresp()

    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        self.voidcmd('TYPE I')
        conn = self.transfercmd(cmd, rest)
        try:
            while 1:
                buf = fp.read(blocksize)
                if not buf: break
                conn.sendall(buf)
                if callback: callback(buf)
            # shutdown ssl layer
            if not self.implicit and isinstance(conn, ssl.SSLSocket):
                conn = conn.unwrap()
        finally:
            conn.close()
        return self.voidresp()

    def storlines(self, cmd, fp, callback=None):
        self.voidcmd('TYPE A')
        conn = self.transfercmd(cmd)
        try:
            while 1:
                buf = fp.readline(self.maxline + 1)
                if len(buf) > self.maxline:
                    raise Error("got more than %d bytes" % self.maxline)
                if not buf: break
                if buf[-2:] != CRLF:
                    if buf[-1] in CRLF: buf = buf[:-1]
                    buf = buf + CRLF
                conn.sendall(buf)
                if callback: callback(buf)
            # shutdown ssl layer
            if not self.implicit and isinstance(conn, ssl.SSLSocket):
                conn = conn.unwrap()
        finally:
            conn.close()
        return self.voidresp()

