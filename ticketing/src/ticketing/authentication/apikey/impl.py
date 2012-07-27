from .interfaces import IAPIKeyEntryResolver, IAPIKeyEntry
from zope.interface import implementer
from .models import APIKey
from sqlalchemy.orm.exc import NoResultFound

@implementer(IAPIKeyEntryResolver)
class DBAPIKeyEntryResolver(object):
    @implementer(IAPIKeyEntry)
    class APIKeyEntry(object):
        def __init__(self, userid_prefix, instance):
            self.userid_prefix = userid_prefix
            self.instance = instance

        @property
        def userid(self):
            return self.userid_prefix + self.instance.apikey

        @property
        def expiry(self):
            return self.instance.expire_at

        @property
        def principals(self):
            return []

    def __init__(self, userid_prefix):
        self.userid_prefix = userid_prefix

    def __call__(self, userid, request):
        if userid is None:
            return None
        if not userid.startswith(self.userid_prefix):
            return None
        try:
            rec = APIKey.query.filter_by(apikey=userid[len(self.userid_prefix):]).one()
            return self.APIKeyEntry(self.userid_prefix, rec)
        except NoResultFound:
            return None

def newDBAPIKeyEntryResolver(userid_prefix):
    return DBAPIKeyEntryResolver(userid_prefix)
