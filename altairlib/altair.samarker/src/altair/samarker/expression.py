from sqlalchemy.sql.expression import Selectable, Executable, ClauseElement, _SelectBase, text, _generative, _clone

class MarkedClauseElement(Executable, ClauseElement):
    __visit_name__ = 'clauselist'
    operator = None

    def __init__(self, inner, comment):
        self.inner = inner
        self.comment = comment
        self.initial = set(dir(self))

    def _copy_internals(self, clone=_clone, **kw):
        self.inner = clone(self.inner, **kw)

    def params(self, *args, **kwargs):
        return self.inner.params(*args, **kwargs)

    def _init_collections(self):
        return self.inner._init_collections()

    def _populate_column_collection(self):
        return self.inner._populate_column_collection()

    @property
    def _columns(self):
        return self.inner._columns

    @_columns.setter
    def _columns(self, value):
        self.inner._columns = value

    @property
    def primary_key(self):
        return self.inner.primary_key

    @primary_key.setter
    def primary_key(self, value):
        self.inner.primary_key = value

    @property
    def foreign_keys(self):
        return self.inner.foreign_keys

    @foreign_keys.setter
    def foreign_keys(self, value):
        self.inner.foreign_keys = value

    @property
    def bind(self):
        return self.inner.bind

    @bind.setter
    def bind(self, bind):
        self.inner.bind = bind 

    def correlate(self, fromclause):
        return self.inner.correlate(fromclause)

    @property
    def _from_objects(self):
        return self.inner._from_objects

    def get_children(self, **kwargs):
        return self.clauses

    @property
    def clauses(self):
        return self.inner, text('/* %s */' % text(self.comment))

    def self_group(self, against=None):
        return self.inner.self_group(against)

class SelectableMarkedClauseElement(MarkedClauseElement, _SelectBase):
    def as_scalar(self):
        return self.inner.as_scalar()

    def apply_labels(self):
        return self.inner.apply_labels()

    def label(self, name):
        return self.as_scalar().label(name)

    def cte(self, name=None, recursive=False):
        return self.inner.cte(name, recursive)

    @property
    def froms(self):
        return self.inner.froms

    @property
    def inner_columns(self):
        return self.inner.inner_columns

    @property
    def _hide_froms(self):
        return self.inner._hide_froms

    @_generative
    def with_hint(self, selectable, text, dialect_name='*'):
        self.inner = self.inner.with_hint(selectable, text, dialect_name)

    @_generative
    def column(self, column):
        self.append_column(column)

    @_generative
    def with_only_columns(self, columns):
        self.inner = self.inner.with_only_columns(columns)

    @_generative
    def where(self, whereclause):
        self.append_whereclause(whereclause)

    @_generative
    def having(self, having):
        self.append_having(having)

    @_generative
    def distinct(self, *expr):
        self.inner = self.inner.distinct(*expr)

    @_generative
    def prefix_with(self, *expr):
        self.inner = self.inner.prefix_with(*expr)

    @_generative
    def select_from(self, fromclause):
        self.inner = self.inner.select_from(fromclause)

    @_generative
    def limit(self, limit):
        self.inner = self.inner.limit(limit)

    @_generative
    def offset(self, offset):
        self.inner = self.inner.offset(offset)

    @_generative
    def order_by(self, *clauses):
        self.inner = self.inner.order_by(*clauses)

    @_generative
    def group_by(self, *clauses):
        self.inner = self.inner.group_by(*clauses)

    def append_correlation(self, fromclause):
        self.inner.append_correlation(fromclause)

    def append_column(self, column):
        self.inner.append_column(column)

    def append_prefix(self, clause):
        self.inner.append_prefix(clause)

    def append_whereclause(self, whereclause):
        self.inner.append_whereclause(whereclause)

    def append_having(self, having):
        self.inner.append_having(having)

    def append_from(self, fromclause):
        self.inner.append_from(fromclause)

    def append_order_by(self, *clauses):
        self.inner.append_order_by(*clauses)

    def append_group_by(self, *clauses):
        self.inner.append_group_by(*clauses)

    def union(self, other, **kwargs):
        return self.__class__(
            self.inner.union(other, **kwargs),
            comment=self.comment
            )

    def union_all(self, other, **kwargs):
        return self.__class__(
            self.inner.union_all(other, **kwargs),
            comment=self.comment
            )

    def except_(self, other, **kwargs):
        return self.__class__(
            self.inner.except_(other, **kwargs),
            comment=self.comment
            )

    def except_all(self, other, **kwargs):
        return self.__class__(
            self.inner.except_all(other, **kwargs),
            comment=self.comment
            )

    def intersect(self, other, **kwargs):
        return self.__class__(
            self.inner.intersect(other, **kwargs),
            comment=self.comment
            )

    def intersect_all(self, other, **kwargs):
        return self.__class__(
            self.inner.intersect_all(other, **kwargs),
            comment=self.comment
            )

def make_marked_clause_element(statement, comment):
    if isinstance(statement, Selectable):
        return SelectableMarkedClauseElement(statement, comment)
    else:
        return MarkedClauseElement(statement, comment)
