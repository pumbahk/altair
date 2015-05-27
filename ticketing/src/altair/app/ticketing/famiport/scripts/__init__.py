from pyramid.paster import bootstrap
from altair.app.ticketing.famiport.datainterchange.filetransfer import FTPSFileSender
from altair.app.ticketing.famiport.datainterchange.interfaces import IFileSender

def includeme(config):
    settings = config.registry.settings
    host = settings['altair.famiport.send_file.ftp.host']
    username = settings['altair.famiport.send_file.ftp.username']
    password = settings['altair.famiport.send_file.ftp.password']
    certificate = settings['altair.famiport.send_file.ftp.certificate']

    sender = FTPSFileSender(host=host, timeout=10, username=username, password=password, ca_certs=certificate)
    config.registry.registerUtility(sender, IFileSender, name='ftps')
