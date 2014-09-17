# This package may contain traces of nuts
import logging
import sqlahelper
import types
from sqlalchemy import orm
from sqlalchemy import schema
from sqlalchemy.sql import expression as expr
from zope.sqlalchemy import ZopeTransactionExtension as _ZTE

logger = logging.getLogger(__name__)
installed = False

def install():
    global installed
    if installed:  # pragma: no cover
        msg = 'logical deleting is already installed!'
        logger.warning(msg)
        return

    logger.debug('install extension for logical deleting')
    sqlahelper._session = orm.scoped_session(
        orm.sessionmaker(class_=LogicalDeletableSession, 
            extension=_ZTE()))
    installed = True

class LogicalDeletableQuery(orm.Query):
    attr_name = 'deleted_at'

    def _compile_context(self, labels=True):
        query = self
        if query._attributes.get('enable_logical_delete', False):
            old_enable_assertions = query._enable_assertions
            query._enable_assertions = False
            context = orm.query.QueryContext(self)
            for e in query._entities:
                e.setup_context(query, context)
            if context.from_clause:
                froms = list(context.from_clause)
            else:
                froms = list(context.froms)

            applied = set()
            def apply(query, t):
                if isinstance(t, expr.Join):
                    if t not in applied:
                        query = apply(query, t.left)
                        query = apply(query, t.right)
                        if isinstance(t.right, expr.Alias):
                            right = t.right.original
                        else:
                            right = t.right
                        if self.attr_name in right.c:
                            t.onclause = expr.and_(t.onclause, t.right.c[self.attr_name] == None)
                        applied.add(t)
                elif isinstance(t, (schema.Table, expr.Alias)):
                    if isinstance(t, expr.Alias):
                        ot = t.original
                    else:
                        ot = t
                    if t not in applied and self.attr_name in ot.c:
                        query = query.filter(t.c[self.attr_name] == None)
                        applied.add(t)
                return query

            for r in context.create_eager_joins:
                if isinstance(r[0], types.MethodType):
                    def _(s):
                        def _create_eager_join(context, entity, path, adapter, parentmapper, clauses, innerjoin):
                            s(context, entity, path, adapter, parentmapper, clauses, innerjoin)
                            # it is possible that the existing eager_joins
                            # get updated by underlying _create_eager_join()
                            # so we need to process the whole on every call.
                            for entity_key in context.eager_joins:
                                join_clause = context.eager_joins[entity_key]
                                context.query = apply(context.query, join_clause)
                                context.eager_joins[entity_key] = join_clause

                        s.im_self._create_eager_join = _create_eager_join
                    _(r[0])

            for t in froms:
                query = apply(query, t)
        retval = super(LogicalDeletableQuery, query)._compile_context(labels)
        query._enable_assertions = old_enable_assertions
        return retval

class LogicalDeletableSession(orm.Session):
    def __init__(self, *args, **kwargs):
        if 'query_cls' not in kwargs:
            kwargs['query_cls'] = LogicalDeletableQuery
        super(LogicalDeletableSession, self).__init__(*args, **kwargs)

    def query(self, *args, **kwargs):
        include_deleted = kwargs.pop('include_deleted', False)
        q = super(LogicalDeletableSession, self).query(*args, **kwargs)
        if not include_deleted:
            q = q.options(LogicalDeletingOption())
        return q

class LogicalDeletingOption(orm.interfaces.MapperOption):
    def process_query(self, query):
        query._attributes['enable_logical_delete'] = True

