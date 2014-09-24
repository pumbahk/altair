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

class StatementProcessor(object):
    def __init__(self, predicate):
        self.predicate = predicate
        self.current_select = None
        self.current_conditions = []
        self.stack = []
        self.applied = set()

    def _visit_join(self, n):
        n.left = self._visit(n.left)
        if isinstance(n.right, expr.Join):
            n.right = self._visit_join(n.right)
        cond = self.predicate(n.right)
        if cond is not None:
            n.onclause = expr.and_(n.onclause, cond)
        return n

    def _visit(self, n):
        if n not in self.applied:
            self.applied.add(n)
            meth = getattr(self, '_visit_%s' % n.__visit_name__, None)
            if meth is not None:
                n = meth(n)
        return n

    def _visit_table(self, n):
        cond = self.predicate(n)
        if cond is not None:
            self.current_conditions.append(cond)
        return n

    def _visit_grouping(self, n):
        n.element = self._visit(n.element)
        return n

    def _visit_alias(self, n):
        return self._visit_table(n)

    def _visit_binary(self, n):
        n.left = self._visit(n.left)
        n.right = self._visit(n.right)
        return n

    def _visit_unary(self, n):
        n.element = self._visit(n.element)
        return n

    def _visit_clauselist(self, n):
        n.clauses = [self._visit(cn) for cn in n.clauses]
        return n

    def _visit_column(self, n):
        n.table = self._visit(n.table)
        return n

    def _visit_select(self, n):
        self.stack.append((self.current_select, self.current_conditions))
        self.current_select = retval = n
        retval._from_obj = [self._visit(cn) for cn in n._from_obj]
        if retval._whereclause is not None:
            retval._whereclause = self._visit(n._whereclause)
        for cond in self.current_conditions:
            retval._whereclause = expr.and_(retval._whereclause, cond)
        (self.current_select, self.current_conditions) = self.stack.pop()
        return retval

    def __call__(self, statement):
        return self._visit(statement)

class LogicalDeletableQuery(orm.Query):
    attr_name = 'deleted_at'

    def _compile_context(self, labels=True):
        retval = super(LogicalDeletableQuery, self)._compile_context(labels)
        if self._attributes.get('enable_logical_delete', False):
            def cond(n):
                if self.attr_name in n.c:
                    return n.c[self.attr_name] == None
                return None
            retval.statement = StatementProcessor(cond)(retval.statement)
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

