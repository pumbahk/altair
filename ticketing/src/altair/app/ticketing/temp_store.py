import hmac
import hashlib
from zope.interface import implementer
from .interfaces import ITemporaryStore
from datetime import datetime

class TemporaryStoreError(Exception):
    pass


@implementer(ITemporaryStore)
class TemporaryCookieStore(object):
    def __init__(self, key, secret, extra_secret_provider=None, applies_to_route=None, **kwargs):
        self.key = key 
        self.secret = secret
        self.extra_secret_provider = extra_secret_provider
        self.applies_to_route = applies_to_route
        self.set_cookie_args = kwargs

    def set(self, request, value):
        if self.extra_secret_provider is not None:
            extra_secret = self.extra_secret_provider(request, value)
            secret = '%s:%s' % (self.secret, extra_secret)
        else:
            secret = self.secret
        digest = hmac.HMAC(
            key=secret,
            msg=value,
            digestmod=hashlib.sha1
            ).hexdigest()
        encoded_value = '%s:%s' % (digest, value)
        kwargs = dict(self.set_cookie_args)
        if self.applies_to_route is not None:
            kwargs['path'] = request.route_path(self.applies_to_route)
        request.response.set_cookie(
            self.key,
            encoded_value,
            **kwargs
            )

    def get(self, request):
        encoded_value = request.cookies[self.key]
        digest, _, value = encoded_value.partition(':')
        if self.extra_secret_provider is not None:
            extra_secret = self.extra_secret_provider(request, value)
            secret = '%s:%s' % (self.secret, extra_secret)
        else:
            secret = self.secret
        calculated_digest = hmac.HMAC(
            key=secret,
            msg=value,
            digestmod=hashlib.sha1
            ).hexdigest()
        if digest != calculated_digest:
            raise TemporaryStoreError('digest mismatch')
        return value

    def clear(self, request):
        if self.key in request.cookies:
            kwargs = {}
            if self.applies_to_route is not None:
                kwargs['path'] = request.route_path(self.applies_to_route)
            request.response.set_cookie(
                self.key,
                '',
                expires=datetime(1970, 1, 1, 0, 0, 0),
                **kwargs
                )
