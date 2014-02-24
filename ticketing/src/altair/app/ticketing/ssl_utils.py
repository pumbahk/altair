from OpenSSL.crypto import load_certificate

def get_certificate_info(request):
    subject_dn = None
    serial = None

    subject_dn_hdr = request.environ.get('HTTP_X_SSL_CLIENT_SUBJECT_DN')
    serial_hdr = request.environ.get('HTTP_X_SSL_CLIENT_SERIAL')
    if subject_dn_hdr is not None and serial_hdr is not None:
        subject_dn = subject_dn_hdr
        try:
            serial = int(serial_hdr)
        except (ValueError, TypeError):
            pass
    else:
        client_cert = request.environ.get('HTTP_X_SSL_CLIENT_CERTIFICATE')
        if client_cert is not None:
            client_cert = re.sub(r'\s+(?!CERTIFICATE)', '\n', client_cert)
            try:
                x509 = load_certificate(FILETYPE_PEM, client_cert)
                subject_dn = ''.join('/%s=%s' % pair for pair in x509.get_subject().get_components())
                serial = x509.get_serial_number()
            except:
                pass
    return subject_dn, serial
