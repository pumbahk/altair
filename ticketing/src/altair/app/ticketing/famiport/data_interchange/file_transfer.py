from ftplib import FTP_TLS
import logging, os

logger = logging.getLogger(__name__)

def send_file_over_ftps(file_path, host, username = None, password = None, upload_dir_path = '/'): # TODO Make it possible to send multiple files?
    ftp = FTP_TLS() # FTP over SSL/TLS
    ftp.set_debuglevel(1) # Moderate amount of debugging output for now

    ftp.connect(host=host, port=21, timeout=600)
    ftp.login(user=username, passwd=password)
    ftp.cwd(upload_dir_path)

    ftp.set_pasv(True) # Enable PASV mode
    ftp.prot_p() # Secure data connection

    file = open(file_path, 'rb')
    file_name = os.path.basename(file.name)
    ftp.storbinary("STOR %s" % file_name, file) # STOR the file with file_name. Override if same file_name exists.
    file.close()

    ftp.quit()
