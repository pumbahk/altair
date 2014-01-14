import hashlib
import hmac
import Cookie

__all__ = [
    'SignedCookie',
    'PlainCookie',
    ]

# Copied from Beaker
class SignedCookie(Cookie.BaseCookie):
    """Extends python cookie to give digital signature support"""
    def __init__(self, secret, input=None):
        self.secret = secret.encode('UTF-8')
        Cookie.BaseCookie.__init__(self, input)

    def value_decode(self, val):
        val = val.strip('"')
        sig = hmac.HMAC(self.secret, val[40:].encode('UTF-8'), hashlib.sha1).hexdigest()

        # Avoid timing attacks
        invalid_bits = 0
        input_sig = val[:40]
        if len(sig) != len(input_sig):
            return None, val

        for a, b in zip(sig, input_sig):
            invalid_bits += a != b

        if invalid_bits:
            return None, val
        else:
            return val[40:], val

    def value_encode(self, val):
        sig = hmac.HMAC(self.secret, val.encode('UTF-8'), hashlib.sha1).hexdigest()
        return str(val), ("%s%s" % (sig, val))

PlainCookie = Cookie.Cookie


