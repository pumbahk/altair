from .interfaces import IMobileCarrierDetector
from . import PC_ACCESS_COOKIE_NAME
from datetime import datetime #ok?
from .interfaces import IMobileCarrierDetector, IMobileRequest

def detect(request):
    return detect_from_wsgi_environment(request.registry, request.environ)

def detect_from_wsgi_environment(registry, environ):
    detector = registry.queryUtility(IMobileCarrierDetector)
    return detector.detect_from_wsgi_environment(environ)

def detect_from_user_agent_string(registry, user_agent):
    detector = registry.queryUtility(IMobileCarrierDetector)
    return detector.detect_from_wsgi_environment({ 'HTTP_USER_AGENT': user_agent })

def detect_from_fqdn(registry, fqdn):
    detector = registry.queryUtility(IMobileCarrierDetector)
    return detector.detect_from_fqdn(fqdn)

def _detect_from_email_address(detector, address):
    try:
        local_part, fqdn = address.split('@', 1)
    except:
        raise ValueError('invalid e-mail address')
    return detector.detect_from_fqdn(fqdn)

def detect_from_email_address(registry, address):
    return _detect_from_email_address(registry.queryUtility(IMobileCarrierDetector), fqdn)

def detect_from_ip_address(registry, address):
    detector = registry.queryUtility(IMobileCarrierDetector)
    return detector.detect_from_ip_address(address)

## smartphone <-> pc switching

## for smartphone
def set_we_need_pc_access(response):
    response.set_cookie(PC_ACCESS_COOKIE_NAME, str(datetime.now()))

def set_we_invalidate_pc_access(response):
    response.delete_cookie(PC_ACCESS_COOKIE_NAME)

def is_mobile(request):
    return IMobileRequest.providedBy(request)

def is_nonmobile(request):
    return not is_mobile(request)
