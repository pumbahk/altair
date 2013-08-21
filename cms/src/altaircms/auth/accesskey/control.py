from altaircms.auth.models import PageAccesskey
from datetime import datetime
import logging
logger = logging.getLogger(__file__)

class PageAccessor(object):
    def __init__(self, page):
        self.page = page

    def filter_with(self, qs):
        return qs.filter_by(page=self.page)

    def generate_with(self, expire=None):
        return PageAccesskey(expiredate=expire, page=self.page)

class EventAccessor(object):
    def __init__(self, event):
        self.event = event

    def filter_with(self, qs):
        return qs.filter_by(event=self.event)

    def generate_with(self, expire=None):
        return PageAccesskey(expiredate=expire, event=self.event)

class AccessKeyControl(object):
    def __init__(self, target, accessor=PageAccessor, request=None):
        self.accessor = accessor(target)
        self.target = target
        self.request = request

    ## delegation
    def publish(self):
        self.target.publish()
    def unpublish(self):
        self.target.unpublish()
    @property
    def published(self):
        return self.target.published
    @property
    def access_keys(self):
        return self.target.access_keys

    ## action
    def get_access_key(self, key):
        if key is None:
            return None
        if getattr(key, "hashkey", None):
            return key
        return self.query_access_key().filter_by(hashkey=key).first()

    def query_access_key(self):
        if self.request:
            qs = self.request.allowable(PageAccesskey)
        else:
            qs = PageAccesskey.query
        return self.accessor.filter_with(qs)

    def expiredate_from_string(self, string, fmt="%Y-%m-%d %H:%M:%S"):
        if string is None:
            return None
        try:
            return datetime.strptime("%Y-%m-%d %H:%M:%S", string)
        except ValueError as e:
            logger.warn(str(e))
        return None

    def create_access_key(self, key=None, expire=None, _genkey=None):
        access_key = self.accessor.generate_with(expire)
        access_key.sethashkey(genkey=_genkey, key=key)
        return access_key

    def delete_access_key(self, target):
        return self.access_keys.remove(target)

    def can_private_access(self, key=None, now=None):
        key = self.get_access_key(key)
        if key is None:
            return False

        if not key in self.access_keys:
            return False
        if key.expiredate is None:
            return True

        now = now or datetime.now()
        return now <= key.expiredate

    def has_access_keys(self):
        return bool(self.access_keys)

    def valid_access_keys(self, _now=None):
        now = _now or datetime.now()
        return [k for k in self.access_keys if k.expiredate >= now]
