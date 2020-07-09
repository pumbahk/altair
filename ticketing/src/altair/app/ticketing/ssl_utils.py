import re
from OpenSSL.crypto import load_certificate
from OpenSSL.crypto import FILETYPE_PEM

import logging
logger = logging.getLogger(__name__)

def get_certificate_info(request):
    subject_dn = None
    serial = None

    subject_dn_hdr = request.environ.get('HTTP_X_SSL_CLIENT_SUBJECT_DN')
    serial_hdr = request.environ.get('HTTP_X_SSL_CLIENT_SERIAL')
    logger.info("[get_certificate_info] start. subject_dn_hdr = {subject_dn_hdr}, serial_hdr = {serial_hdr}"
                .format(subject_dn_hdr=subject_dn_hdr, serial_hdr=serial_hdr))
    if subject_dn_hdr is not None and serial_hdr is not None:
        subject_dn = subject_dn_hdr
        try:
            serial = int(serial_hdr, 16)
        except (ValueError, TypeError) as e:
            logger.exception("int(serial_hdr, 16) error = {}".format(e))
            pass
    else:
        client_cert = request.environ.get('HTTP_X_SSL_CLIENT_CERTIFICATE')
        logger.info("[get_certificate_info] client_cert = {}".format(client_cert))
        if client_cert is not None:
            client_cert = re.sub(r'\s+(?!CERTIFICATE)', '\n', client_cert)
            try:
                x509 = load_certificate(FILETYPE_PEM, client_cert)
                subject_dn = ''.join('/%s=%s' % pair for pair in x509.get_subject().get_components())
                serial = x509.get_serial_number()
            except Exception as e:
                logger.exception("client_cert process is failed. {}".format(e))
                pass
    logger.info("[get_certificate_info] end.  subject_dn_hdr = {subject_dn_hdr}, serial_hdr = {serial_hdr}"
                .format(subject_dn_hdr=subject_dn_hdr, serial_hdr=serial_hdr))
    return subject_dn, serial
