import logging
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy.orm.interfaces import MapperOption
from zope.sqlalchemy import ZopeTransactionExtension as _ZTE

logger = logging.getLogger(__name__)


def install():
    logger.debug('install extension for logical deleting')
    sqlahelper._session = orm.scoped_session(
        orm.sessionmaker(class_=LogicalDeletableSession, 
            extension=_ZTE()))

class LogicalDeletableQuery(orm.Query):
    def filter(self, *args, **kwargs):
        q = super(LogicalDeletableQuery, self).filter(*args, **kwargs)

        condition = args[0]
        for side in ('left', 'right'):

            if hasattr(condition, side):
                operand = getattr(condition, side)
                if hasattr(operand, "table"):
                    if hasattr(operand.table.c, "deleted_at"):
                        q = orm.Query.filter(q, operand.table.c.deleted_at==None)
        return q

class LogicalDeletableSession(orm.Session):
    def __init__(self, *args, **kwargs):
        kwargs.update(query_cls=LogicalDeletableQuery)
        super(LogicalDeletableSession, self).__init__(*args, **kwargs)

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

