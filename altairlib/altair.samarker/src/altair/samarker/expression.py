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

    def append_order_by(self, *clauses):
        self.inner.append_order_by(*clauses)

    def append_group_by(self, *clauses):
        self.inner.append_group_by(*clauses)

    @property
    def _hide_froms(self):
        return self.inner._hide_froms

def make_marked_clause_element(statement, comment):
    if isinstance(statement, Selectable):
        return SelectableMarkedClauseElement(statement, comment)
    else:
        return MarkedClauseElement(statement, comment)
