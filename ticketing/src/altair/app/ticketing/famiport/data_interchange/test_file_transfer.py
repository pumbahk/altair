import unittest
import mock

class FTPSFileSenderTest(unittest.TestCase):
    def setUp(self):
        self.ftp_tls = mock.Mock()

    def _makeOne(self, *args, **kwargs):
        from .file_transfer import FTPSFileSender
        retval = FTPSFileSender(*args, **kwargs)
        retval.FTP_TLS = lambda *args, **kwargs: self.ftp_tls
        return retval

    def test_send_file_basic(self):
        from io import BytesIO
        target = self._makeOne(
            host='localhost',
            port=12345
            )
        f = BytesIO("test")
        target.send_file('/remote/path/file', f)
        self.ftp_tls.cwd.assert_called_with('/remote/path')
        self.ftp_tls.storbinary.assert_called_with('STOR file', f)
