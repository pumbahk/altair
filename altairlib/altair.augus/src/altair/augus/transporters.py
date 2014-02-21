#-*- coding: utf-8 -*-
import os.path
import ftplib
import ftputil

class _Transporter(object):
    pass

def reconnect(func):
    def _wrap(self, *args, **kwds):
        if not self.is_connect:
            self.connect()
        return func(self, *args, **kwds)
    return _wrap

class FTPTransporter(_Transporter):
    def __init__(self, hostname, username, password, passive=False):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.passive = passive
        self._conn = None

    def _create_session(self, *args, **kwds):
        session = ftplib.FTP(*args, **kwds)
        session.set_pasv(self.passive) # self... (--;)
        return session

    def connect(self):
        if not self.is_connect:
            self._conn = ftputil.FTPHost(
                self.hostname, self.username, self.password,
                session_factory=self._create_session)

    def disconnect(self):
        self._conn = None

    @property
    def is_connect(self):
        return self._conn

    @reconnect
    def chdir(self, path):
        self._conn.chdir(path)

    @reconnect
    def get(self, src, dst, remove=False, force=False):
        download = self._conn.download if force else self._conn.download_if_newer
        status = download(src, dst)
        if status and remove: # success
            status = self.remove(src, force=force)
        return status

    @reconnect
    def put(self, src, dst, parents=False, force=False):
        # mkdir -p
        if parents:
            dirname = os.path.dirname(dst)
            self.makedirs(dirname)

        # upload
        upload = self._conn.upload if force else self._conn.upload_if_newer
        return upload(src, dst)

    @reconnect
    def remove(self, path, recursive=False, force=False):
        assert recursive is False, 'oh no, not imprement yet (--;)'
        try:
            return self._conn.remove(path)
        except:
            if force:
                return False
            else:
                raise
    @reconnect
    def makedirs(self, path):
        return self._conn.makedirs(path)

    @reconnect
    def listdir(self, path=None):
        path = self._conn.curdir if path is None else path
        return self._conn.listdir(path)
