import logging
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy.orm.interfaces import MapperOption
from zope.sqlalchemy import ZopeTransactionExtension as _ZTE

logger = logging.getLogger(__name__)


def install():
    sqlahelper._session = orm.scoped_session(
        orm.sessionmaker(class_=LogicalDeletableSession, 
            extension=_ZTE()))

class LogicalDeletableSession(orm.Session):
    def query(self, *args, **kwargs):
        q = super(LogicalDeletableSession, self).query(*args, **kwargs)
        option = LogicalDeletingOption("deleted_at")
        return option._process(q)

class LogicalDeletingOption(MapperOption):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def process_query(self, query):
        self._process(query)

    def process_query_conditionally(self, query):
        self._process(query)


    def _process(self, query):
        
        _query = query
        assert query._entities
        for e in  query._entities:
            if hasattr(e.type, self.attr_name):
                query = query.filter(getattr(e.type, self.attr_name)==None)
            elif hasattr(e, 'actual_froms'):
                for t in e.actual_froms:
                    if hasattr(t.c, self.attr_name):
                        query = query.filter(getattr(t.c, self.attr_name)==None)
        _query._criterion = query._criterion
        _query._enable_assertions = False
        return _query

