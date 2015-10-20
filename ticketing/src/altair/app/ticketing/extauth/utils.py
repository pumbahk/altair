from os import urandom
import hashlib
import six
from altair.mobile.interfaces import IMobileRequest
from altair.oauth.response import OAuthResponseRenderer

ALNUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def get_oauth_response_renderer(request):
    if IMobileRequest.providedBy(request):
        encoding = request.io_codec
    else:
        encoding = 'utf-8'
    return OAuthResponseRenderer(encoding)

def generate_salt():
    return u''.join('%02x' % six.byte2int(c) for c in urandom(16))

def generate_random_alnum_string(n):
    return u''.join(ALNUM[six.byte2int(c) % len(ALNUM)] for c in urandom(n))

def digest_secret(secret, salt):
    assert len(salt) == 32
    h = hashlib.sha256()
    h.update(salt + secret)
    return salt + h.hexdigest()

def period_overlaps(a, b):
    return ((a[0] is None or (b[0] is not None and a[0] <= b[0])) and
        (a[1] is None or (b[0] is not None and b[0] <= a[1]))) \
       or ((a[0] is None or (b[1] is not None and a[0] <= b[1])) and
           (a[1] is None or (b[1] is not None and b[1] <= a[1])))

