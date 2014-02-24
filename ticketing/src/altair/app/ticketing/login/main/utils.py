from altair.app.ticketing.ssl_utils import get_certificate_info

def get_auth_identifier_from_client_certified_request(request):
    subject_dn, serial = get_certificate_info(request)
    if subject_dn is not None:
        return '%s:%s' % (subject_dn, serial)
    return None

