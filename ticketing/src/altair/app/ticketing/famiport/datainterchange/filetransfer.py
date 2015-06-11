# -*- coding:utf-8 -*-

from zope.interface import implementer, provider
from ftplib_ import FTP_TLS_ as FTP_TLS
from enum import IntEnum
import logging, os
from datetime import datetime
from .interfaces import IFileSender, IFileSenderFactory

logger = logging.getLogger(__name__)

@provider(IFileSenderFactory)
@implementer(IFileSender)
class FTPSFileSender(object):
    FTP_TLS = FTP_TLS

    def __init__(self, host, port=21, timeout=600, username=None, password=None, ca_certs = None, passive=True, debuglevel=1):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password
        self.ca_certs = ca_certs
        self.passive = passive
        self.debuglevel = debuglevel

    def send_file(self, remote_path, file):
        remote_dir = os.path.dirname(remote_path)
        remote_file = os.path.basename(remote_path)

        logger.info('uploading file to %s' % remote_path)

        ftp = self.FTP_TLS(ca_certs=self.ca_certs) # FTP over SSL/TLS
        ftp.set_debuglevel(self.debuglevel)

        logger.info('trying to connect to %s:%d' % (self.host, self.port))
        ftp.connect(host=self.host, port=self.port, timeout=self.timeout)
        try:
            ftp.login(user=self.username, passwd=self.password)
            if remote_dir: # change directory if needed
                ftp.cwd(remote_dir)

            ftp.set_pasv(self.passive) # Enable PASV mode
            ftp.prot_p() # Secure data connection

            ftp.storbinary("STOR %s" % remote_file, file) # STOR the file with file_name. Override if same file_name exists.
            logger.info('file successfully sent as %s' % remote_path)
        finally:
            try:
                ftp.quit()
            except:
                logger.exception('exception ignored')

class FamiPortFileType(IntEnum):
    SALES = 0
    REFUND = 1

class FamiPortFileManager(object):

    def __init__(self, registry, file_type=FamiPortFileType.SALES):
        self.registry = registry
        assert(isinstance(file_type, FamiPortFileType))
        self.file_type = file_type
        self.file_path = None
        stage_dir_name = 'altair.famiport.' + self.file_type._name_.lower() + '.stage.dir'
        sent_dir_name = 'altair.famiport.' + self.file_type._name_.lower() + '.sent.dir'
        pending_dir_name = 'altair.famiport.' + self.file_type._name_.lower() + '.pending.dir'
        self.stage_dir = registry.settings[stage_dir_name]
        self.sent_dir = registry.settings[sent_dir_name]
        self.pending_dir = registry.settings[pending_dir_name]
        self.upload_dir_path = registry.settings['altair.famiport.send_file.ftp.upload_dir_path']
        self.host = registry.settings['altair.famiport.send_file.ftp.host']
        self.username = registry.settings['altair.famiport.send_file.ftp.username']
        self.password = registry.settings['altair.famiport.send_file.ftp.password']
        self.certificate = registry.settings['altair.famiport.send_file.ftp.certificate']

    def send_staged_file(self, file_type=None):
        latest_stage_dir = self.get_latest_stage_dir(datetime.now())
        assert(isinstance(file_type, FamiPortFileType))

        file_name = None
        if file_type == FamiPortFileType.SALES:
            file_name = 'SAL_DAT.txt'
        elif file_type == FamiPortFileType.REFUND:
            file_name = 'REF_DAT.txt'

        self.file_path = os.path.join(latest_stage_dir, file_name)

        sender = FTPSFileSender(host=self.host, username=self.username, password=self.password, ca_certs=self.certificate)
        if not os.path.exists(self.file_path):
            raise Exception('%s does not exist' % self.file_path)
        else:
            with open(self.file_path) as file:
                sender.send_file(os.path.join(self.upload_dir_path, file_name), file)

        # 転送完了フラグファイルの送信
        transfer_complete_filename = None
        if file_type == FamiPortFileType.SALES:
            transfer_complete_filename = 'SAL_DAT_FLG.txt'
        elif file_type == FamiPortFileType.REFUND:
            transfer_complete_filename = 'REF_DAT_FLG.txt'
        with open (transfer_complete_filename, 'w+') as file: # Create one if not exist
            sender.send_file(os.path.join(self.upload_dir_path, transfer_complete_filename), file)

    def get_latest_stage_dir(self, now=datetime.now()):
        work_dir = os.path.join(self.stage_dir, now.strftime("%Y%m%d"))
        if not os.path.exists(work_dir):
            return None
        return work_dir

    def mark_file_sent(self):
        if not self.file_path or not self.file_path.startswith(self.stage_dir):
            raise ValueError("specified file (%s) does not exist under %s" % (self.file_path, self.stage_dir))
        vpart = os.path.dirname(self.file_path[len(self.stage_dir):]).lstrip('/')
        sent_dir = os.path.join(self.sent_dir, vpart)
        if not os.path.exists(sent_dir):
            os.makedirs(sent_dir)
        os.rename(self.file_path, os.path.join(sent_dir, os.path.basename(self.file_path)))

    def mark_file_pending(self):
        if not self.file_path or not self.file_path.startswith(self.stage_dir):
            raise ValueError("specified file (%s) does not exist under %s" % (self.file_path, self.stage_dir))
        vpart = os.path.dirname(self.file_path[len(self.stage_dir):]).lstrip('/')
        pending_dir = os.path.join(self.pending_dir, vpart)
        if not os.path.exists(pending_dir):
            os.makedirs(pending_dir)
        os.rename(self.file_path, os.path.join(pending_dir, os.path.basename(self.file_path)))
