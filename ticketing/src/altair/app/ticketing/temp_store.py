import hmac
import hashlib
from zope.interface import implementer
from .interfaces import ITemporaryStore
from datetime import datetime
from urlparse import urlparse

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
            # path may contain a query portion ?session=XXX
            kwargs['path'] = urlparse(request.route_path(self.applies_to_route)).path
        request.response.set_cookie(
            self.key,
            encoded_value,
            **kwargs
            )

    def get(self, request):
        encoded_value = request.cookies.get(self.key)
        if encoded_value is None:
            raise TemporaryStoreError('no such cookie: %s' % self.key)
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
        if self.applies_to_route is not None:
            path = request.route_path(self.applies_to_route)
            # path may contain a query portion ?session=XXX
            path = urlparse(path).path
        else:
            path = self.set_cookie_args.get('path')
        if self.key in request.cookies or path is not None:
            kwargs = {}
            if path is not None:
                kwargs['path'] = path
            request.response.set_cookie(
                self.key,
                '',
                expires=datetime(1970, 1, 1, 0, 0, 0),
                **kwargs
                )
