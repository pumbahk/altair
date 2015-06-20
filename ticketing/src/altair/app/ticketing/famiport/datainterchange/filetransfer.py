# -*- coding:utf-8 -*-

import os
import re
import logging
from io import BytesIO
from datetime import datetime
from zope.interface import implementer, provider
from ftplib_ import FTP_TLS_ as FTP_TLS
from enum import IntEnum
from .interfaces import IFileSender, IFileSenderFactory, IFamiPortFileManagerFactory
from .utils import make_room

logger = logging.getLogger(__name__)

@provider(IFileSenderFactory)
@implementer(IFileSender)
class FTPSFileSender(object):
    FTP_TLS = FTP_TLS

    def __init__(self, host, port=21, timeout=600, username=None, password=None, ca_certs = None, passive=True, debuglevel=0):
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
    host_port_pair = settings['%s.host' % prefix]
    m = re.match(ur'^(?:([^:]+)(?::([^:]+))?|(\[[^]]+\])(?::([^:]+))?)$', host_port_pair)
    try:
        host = m.group(1) or m.group(3)
        port = int(m.group(2) or m.group(4) or 990)
    except:
        raise ValueError('invalid host name: %s' % host_port_pair)
    username = settings['%s.username' % prefix]
    password = settings['%s.password' % prefix]
    certificate = settings.get('%s.certificate' % prefix, None)
    return FTPSFileSender(host=host, port=port, username=username, password=password, ca_certs=certificate)


class FamiPortFileManager(object):
    def __init__(self, sender, filename, transfer_complete_filename, stage_dir, sent_dir, pending_dir, upload_dir_path, **kwargs):
        self.sender = sender
        self.filename = filename
        self.transfer_complete_filename = transfer_complete_filename
        self.stage_dir = stage_dir
        self.sent_dir = sent_dir
        self.pending_dir = pending_dir
        self.upload_dir_path = upload_dir_path

    def send_staged_file(self):
        latest_stage_dir = self.get_latest_stage_dir(datetime.now())
        if latest_stage_dir is None:
            logger.info('nothing to do') 
            return

        filename = self.filename
        file_path = os.path.join(latest_stage_dir, filename)

        sender = self.sender
        if not os.path.exists(file_path):
            raise Exception('%s does not exist' % file_path)
        try:
            with open(file_path) as file:
                if self.upload_dir_path is not None:
                    path = os.path.join(self.upload_dir_path, filename)
                else:
                    path = filename
                sender.send_file(path, file)

            # 転送完了フラグファイルの送信
            f = BytesIO()
            if self.upload_dir_path is not None:
                sender.send_file(os.path.join(self.upload_dir_path, self.transfer_complete_filename), f)
            else:
                sender.send_file(self.transfer_complete_filename, f)
            self.mark_as_sent(latest_stage_dir)
        except:
            self.mark_as_pending(latest_stage_dir)
            raise

    def get_latest_stage_dir(self, now=datetime.now()):
        work_dir = os.path.join(self.stage_dir, now.strftime("%Y%m%d"))
        if not os.path.exists(work_dir):
            logger.info('%s not found' % work_dir)
            return None
        return work_dir

    def mark_as_sent(self, dir_):
        vpart = os.path.basename(dir_)
        sent_dir = os.path.join(self.sent_dir, vpart)
        make_room(sent_dir)
        os.rename(dir_, sent_dir)

    def mark_as_pending(self, dir_):
        vpart = os.path.basename(dir_)
        pending_dir= os.path.join(self.pending_dir, vpart)
        make_room(pending_dir)
        os.rename(dir_, pending_dir)

