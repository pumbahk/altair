from zope.interface import implementer, provider
from ftplib_ import FTP_TLS_ as FTP_TLS
import logging, os
import ssl
from .interfaces import IFileSender, IFileSenderFactory

logger = logging.getLogger(__name__)

@provider(IFileSenderFactory)
@implementer(IFileSender)
class FTPSFileSender(object):

    def __init__(self, host, port=21, timeout=600, username=None, password=None, certfile = None, passive=True, debuglevel=1):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password
        self.certfile = certfile
        self.passive = passive
        self.debuglevel = debuglevel

    def send_file(self, remote_path, f): # TODO Make it possible to send multiple files?
        remote_dir = os.path.dirname(remote_path)
        remote_file = os.path.basename(remote_path)

        logger.info('uploading file to %s' % remote_path)

        ftp = FTP_TLS(ca_certs=self.certfile) # FTP over SSL/TLS
        ftp.set_debuglevel(self.debuglevel) # Moderate amount of debugging output for now

        logger.info('trying to connect to %s:%d' % (self.host, self.port))
        ftp.connect(host=self.host, port=self.port, timeout=self.timeout)
        try:
            ftp.login(user=self.username, passwd=self.password)
            ftp.cwd(remote_dir)

            ftp.set_pasv(self.passive) # Enable PASV mode
            ftp.prot_p() # Secure data connection

            ftp.storbinary("STOR %s" % remote_file, f) # STOR the file with file_name. Override if same file_name exists.
            logger.info('file successfully sent as %s' % remote_path)
        finally:
            try:
                ftp.quit()
            except:
                logger.exception('exception ignored')
