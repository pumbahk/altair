import six
from zope.interface import implementer
from dogpile.cache.region import NO_VALUE
from datetime import timedelta
from .interfaces import IPersistentStore

@implementer(IPersistentStore)
class DogpileBackedPersistentStore(object):
    def __init__(self, region, expiration_time=None, encoding='utf-8'):
        self.region = region
        self._expiration_time = expiration_time
        self.encoding = encoding

    def _normalize_key(self, k):
        if isinstance(k, six.text_type):
            k = k.encode(self.encoding)
        return k

    @property
    def expiration_time(self):
        retval = self._expiration_time if self._expiration_time is not None else self.region.expiration_time
        if not isinstance(retval, timedelta):
            retval = timedelta(seconds=retval)
        return retval

    def __getitem__(self, k):
        k = self._normalize_key(k)
        v = self.region.get(k, expiration_time=self._expiration_time)
        if v is NO_VALUE:
            raise KeyError(k)
        return v

    def __setitem__(self, k, v):
        k = self._normalize_key(k)
        self.region.set(k, v)

    def __contains__(self, k):
        k = self._normalize_key(k)
        v = self.region.get(k, expiration_time=self._expiration_time)
        return v is not NO_VALUE

    def __delitem__(self, k):
        k = self._normalize_key(k)
        self.region.delete(k)
