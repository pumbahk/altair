# -*- coding:utf-8 -*-

from zope.interface import implementer, provider
from ftplib_ import FTP_TLS_ as FTP_TLS
from enum import IntEnum
import logging, os
from datetime import datetime
from .interfaces import IFileSender, IFileSenderFactory, IFamiPortFileManagerFactory

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

            ftp.storbinary("STOR %s" % remote_file, file) # STOR the file with filename. Override if same filename exists.
            logger.info('file successfully sent as %s' % remote_path)
        finally:
            try:
                ftp.quit()
            except:
                logger.exception('exception ignored')


@implementer(IFamiPortFileManagerFactory)
class FamiPortFileManagerFactory(object):
    default_file_type_mappings = {
        'sales': dict(
            filename='SAL_DAT.txt',
            transfer_complete_filename='SAL_DAT_FLG.txt'
            ),
        'refund': dict(
            filename='REF_DAT.txt',
            transfer_complete_filename='REF_DAT_FLG.txt'
            )
        }

    def __init__(self, sender, settings_prefix='altair.famiport'):
        self.sender = sender
        self.configurations = {}
        self.settings_prefix = settings_prefix

    def add_configuration_from_settings(self, type, settings):
        default_file_type_mapping = self.default_file_type_mappings.get(type)

        stage_dir_name = '%s.%s.stage.dir' % (self.settings_prefix, type)
        sent_dir_name = '%s.%s.sent.dir' % (self.settings_prefix, type)
        pending_dir_name = '%s.%s.pending.dir' % (self.settings_prefix, type)
        upload_dir_path_name = '%s.%s.upload.dir' % (self.settings_prefix, type)
        filename_name = '%s.%s.filename' % (self.settings_prefix, type)
        encoding_name = '%s.%s.encoding' % (self.settings_prefix, type)
        eor_name = '%s.%s.eor' % (self.settings_prefix, type)
        transfer_complete_filename_name = '%s.%s.transfer_complete_filename' % (self.settings_prefix, type)

        self.configurations[type] = dict( 
            stage_dir=settings[stage_dir_name],
            sent_dir=settings[sent_dir_name],
            pending_dir=settings[pending_dir_name],
            upload_dir_path=settings.get(upload_dir_path_name, None),
            filename=settings.get(filename_name, default_file_type_mapping and default_file_type_mapping['filename']),
            transfer_complete_filename=settings.get(transfer_complete_filename_name, default_file_type_mapping and default_file_type_mapping['transfer_complete_filename']),
            encoding=settings.get(encoding_name),
            eor=settings.get(eor_name)
            )

    def get_configuration(self, type):
        return self.configurations[type]

    def __call__(self, type, **overrides):
        configuration = self.configurations[type]
        if overrides:
            configuration = dict(configuration)
            configuration.update(overrides)
        return FamiPortFileManager(sender=self.sender, **configuration)


def create_ftps_file_sender_from_settings(settings, prefix='altair.famiport.send_file.ftp'):
    host = settings['%s.host' % prefix]
    username = settings['%s.username' % prefix]
    password = settings['%s.password' % prefix]
    certificate = settings.get('%s.certificate' % prefix, None)
    return FTPSFileSender(host=host, username=username, password=password, ca_certs=certificate)


class FamiPortFileManager(object):
    def __init__(self, sender, filename, transfer_complete_filename, stage_dir, sent_dir, pending_dir, upload_dir_path, **kwargs):
        self.sender = sender
        self.filename = filename
        self.transfer_complete_filename = transfer_complete_filename
        self.stage_dir = stage_dir
        self.sent_dir = sent_dir
        self.pending_dir = pending_dir
        self.upload_dir_path = upload_dir_path
        self.file_path = None

    def send_staged_file(self):
        latest_stage_dir = self.get_latest_stage_dir(datetime.now())

        filename = self.filename
        self.file_path = os.path.join(latest_stage_dir, filename)

        sender = self.sender
        if not os.path.exists(self.file_path):
            raise Exception('%s does not exist' % self.file_path)
        else:
            with open(self.file_path) as file:
                if self.upload_dir_path is not None:
                    path = os.path.join(self.upload_dir_path, filename)
                else:
                    path = filename
                sender.send_file(path, file)

        # 転送完了フラグファイルの送信
        transfer_complete_filename = None
        with open (transfer_complete_filename, 'w+') as file: # Create one if not exist
            sender.send_file(os.path.join(self.upload_dir_path, transfer_complete_filename), file)

    def get_latest_stage_dir(self, now=datetime.now()):
        work_dir = os.path.join(self.stage_dir, now.strftime("%Y%m%d"))
        if not os.path.exists(work_dir):
            raise Exception('%s does not exist' % work_dir)
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
