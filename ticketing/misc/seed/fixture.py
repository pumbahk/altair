# encoding: utf-8
import operator
import logging
import re
import datetime
from itertools import chain
from types import FunctionType

ESCAPE_TABLE = {
    u"\a": u"\\a",
    u"\b": u"\\b",
    u"\f": u"\\f",
    u"\n": u"\\n",
    u"\r": u"\\r",
    u"\t": u"\\t",
    u"\v": u"\\v",
    }

def litescape(s):
    def escape_char(c):
        retval = ESCAPE_TABLE.get(c)
        if retval is not None:
            return retval
        return u"\\u%04x" % ord(c)

    return re.sub(ur"[\x00-\x1f\\\xff]", lambda m: escape_Char(m.groups(0)), s)

def _repr(item):
    if isinstance(item, unicode):
        return "u'%s'" % litescape(item.encode('utf-8'))
    else:
        return repr(item)

class rel(object):
    def __init__(self, collection, referencing_fields=None, other_side_fields=None, schema=None):
        self.collection = collection
        if referencing_fields is None:
            self.referencing_fields = ()
        elif isinstance(referencing_fields, basestring):
            self.referencing_fields = (referencing_fields, )
        else:
            self.referencing_fields = tuple(referencing_fields)

        if other_side_fields is None:
            self.other_side_fields = None
        elif isinstance(other_side_fields, basestring):
            self.other_side_fields = (other_side_fields, )
        else:
            self.other_side_fields = tuple(other_side_fields)
        self.schema = schema

    def __getitem__(self, k):
        return self.collection[k]

    def __setitem__(self, k, v):
        self.collection[k] = v

    def __len__(self):
        return len(self.collection)

    def __iter__(self):
        return iter(self.collection)

    def __repr__(self):
        return 'rel(..., %s)' % ', '.join(_repr(item) for item in (self.referencing_fields, self.other_side_fields, self.schema) if item is not None)

class auto(tuple):
    def __new__(self, args):
        return tuple.__new__(self, (args, ))

class Data(object):
    def __init__(self, schema, id_fields, **fields):
        self._schema = schema
        if isinstance(id_fields, basestring):
            self._id_fields = (id_fields, )
        elif isinstance(id_fields, tuple):
            self._id_fields = id_fields
        else:
            self._id_fields = tuple(id_fields)
        self._fields = {}
        for k, v in fields.iteritems():
            setattr(self, k, v)

    @property
    def _id(self):
        return tuple(getattr(self, k) for k in self._id_fields)

    def __setattr__(self, k, v):
        if k.startswith('_'):
            object.__setattr__(self, k, v)
        else:
            object.__getattribute__(self, '_fields')[k] = v

    def __getattr__(self, k):
        try:
            return object.__getattribute__(self, '_fields')[k]
        except KeyError:
            raise AttributeError('%s.%s' % (self._schema, k))

    def __eq__(self, that):
        return id(self) == id(that)

    def __hash__(self):
        return object.__hash__(self)

    def __repr__(self):
        return 'Data(%r, %r, %s)' % (self._schema, self._id_fields, ', '.join('%s=%s' % (pair[0], '...' if isinstance(pair[1], rel) else _repr(pair[1])) for pair in self._fields.iteritems()))

class DataSet(object):
    logger = logging.getLogger('fixture.DataSet')

    def __init__(self, schema):
        self.schema = schema
        self.data = set()
        self.seq = 1

    def add(self, data):
        if data in self.data:
            return False

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('Trying to add %s' % data)

        if isinstance(data._id_fields, auto):
            setattr(data, data._id_fields[0], self.seq)
            self.seq += 1
        self.data.add(data)
        return True

    def get(self):
        return sorted(iter(self.data),
            lambda a, b: \
                cmp(getattr(a, a._id_fields[0]), getattr(b, b._id_fields[0])) \
                if a._id_fields and b._id_fields else 0)

    def __iter__(self):
        return iter(self.get())
 
class DataSuite(object):
    def __init__(self):
        self.datasets = {}

    def __getitem__(self, schema):
        dataset = self.datasets.get(schema)
        if dataset is None:
            dataset = DataSet(schema)
            self.datasets[schema] = dataset
        return dataset

    def __iter__(self):
        return self.datasets.itervalues()

class ReferenceGraph(object):
    def __init__(self):
        self.references = {}
        self.back_references = {}
        self.weight_cache = None

    def add_reference(self, referencing, referenced):
        references = self.references.setdefault(referencing, set())
        if referenced is not None:
            references.add(referenced)
            self.back_references.setdefault(referenced, set()).add(referencing)
        self.weight_cache = None

    def get_weight(self, referenced):
        return self._get_weight(referenced, set())

    def _get_weight(self, referenced, seen):
        if self.weight_cache is not None:
            weight = self.weight_cache.get(referenced)
            if weight is not None:
                return weight
        if referenced in seen:
            return 0
        seen.add(referenced)
        weight = 1
        back_references = self.back_references.get(referenced)
        if back_references is not None:
            for referencing in back_references:
                weight += self._get_weight(referencing, seen)
        if self.weight_cache is None:
            self.weight_cache = {}
        self.weight_cache[referenced] = weight
        return weight

    def getlist(self):
        return sorted(self.references.iterkeys(),
                lambda a, b: \
                    cmp(self.get_weight(a),
                         self.get_weight(b)))

class DataWalker(object):
    logger = logging.getLogger('fixture.DataWalker')

    def __init__(self, suite, digraph):
        self.suite = suite
        self.digraph = digraph

    def __call__(self, data):
        dataset = self.suite[data._schema]
        if dataset.add(data):
            self.digraph.add_reference(data._schema, None)
            for name, value in data._fields.iteritems():
                if isinstance(value, rel):
                    if value.schema is None:
                        try:
                            first = iter(value).next()
                            self.digraph.add_reference(first._schema, data._schema)
                            for _data in iter(value):
                                self(_data)
                                for k1, k2 in zip(value.referencing_fields, data._id_fields):
                                    setattr(_data, k1, getattr(data, k2))
                        except StopIteration:
                            pass
                    else:
                        first = None
                        try:
                            first = iter(value).next()
                        except StopIteration:
                            pass
                        self.digraph.add_reference(value.schema, data._schema)
                        if first is not None:
                            self.digraph.add_reference(value.schema, first._schema)
                        for _data in iter(value):
                            self(_data)
                            these_field_values = tuple(getattr(data, field) for field in data._id_fields)
                            those_field_values = tuple(getattr(_data, field) for field in _data._id_fields)
                            if len(these_field_values) != len(value.referencing_fields):
                                raise Exception("number of referencing fields must be identical to the referenced data's id fields")
                            if len(those_field_values) != len(value.other_side_fields):
                                raise Exception("number of other side's fields must be identical to the other side's data's id fields")
                            intermediate_datum = Data(
                                value.schema,
                                value.referencing_fields + value.other_side_fields,
                                **dict(
                                    chain(
                                        zip(value.referencing_fields, these_field_values),
                                        zip(value.other_side_fields, those_field_values)
                                        )
                                    )
                                )
                            self(intermediate_datum)
                elif isinstance(value, Data):
                    self(value)
                    self.digraph.add_reference(data._schema, value._schema)
                elif not isinstance(value, basestring) and value is not None:
                    collection_iter = None
                    try:
                        collection_iter = iter(value)
                    except:
                        pass
                    if collection_iter is not None:
                        for _data in collection_iter:
                            self(_data)
        return data

class InsertStmtBuilder(object):
    def __init__(self, builder):
        self.builder = builder
        self.prev_table = None
        self.prev_keys = u''
        self.nbytes_sent = 0

    def flush(self):
        if self.prev_table is not None:
            self.write(";\n");
        self.prev_table = None
        self.prev_keys = u''
        self.nbytes_sent = 0

    def write(self, str):
        self.builder.out.write(str)
        self.nbytes_sent += len(str)

    def __call__(self, table, _values):
        encoding = self.builder.encoding
        values = []
        keys = u''
        value_len = 0
        for k, v in _values:
            v_ = self.builder.put_scalar(v)
            keys += k
            values.append((k, v_))
            value_len += len(v_)

        if self.nbytes_sent >= 131072:
            self.flush() 

        if self.prev_table != table or self.prev_keys != keys:
            self.flush()
            self.write("INSERT INTO %s (%s) VALUES\n" % (
                table.encode(encoding),
                ', '.join(self.builder.put_identifier(k) for k, v in values)))
        else:
            self.write(",\n")

        if value_len < 1024:
            self.write("(" + ", ".join(v for _, v in values) + ")")
        else:
            self.write("(")
            first = True
            for _, v in values:
                if not first:
                    self.write(", ")
                self.write(v)
                first = False
            self.write(")")
        self.prev_table = table
        self.prev_keys = keys

class SQLBuilder(object):
    def __init__(self, out, encoding=None):
        self.out = out
        self.encoding = encoding or self.out.encoding
        self.last_stmt = None

    def __del__(self):
        self.flush()

    def put_identifier(self, name):
        if isinstance(name, str):
            return "`%s`" % name
        elif isinstance(name, unicode):
            return "`%s`" % name.encode(self.encoding)
        else:
            raise Exception("Unsupported type: " + type(name).__name__)

    def put_scalar(self, scalar):
        if isinstance(scalar, str):
            return "'%s'" % scalar.replace("'", "''")
        elif isinstance(scalar, unicode):
            return "'%s'" % scalar.replace(u"'", u"''").encode(self.encoding)
        elif isinstance(scalar, datetime.datetime):
            return "'%s'" % scalar.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(scalar, datetime.date):
            return "'%s'" % scalar.strftime("%Y-%m-%d")
        elif isinstance(scalar, datetime.time):
            return "'%s'" % scalar.strftime("%H:%M:%S")
        elif isinstance(scalar, (float, int, long)):
            return '%d' % scalar
        elif scalar is None:
            return 'NULL'
        else:
            raise Exception("Unsupported type: " + type(scalar).__name__)

    def insert(self, table, values):
        if not isinstance(self.last_stmt, InsertStmtBuilder):
            if self.last_stmt is not None:
                self.last_stmt.flush()
            self.last_stmt = InsertStmtBuilder(self)
        self.last_stmt(table, values)

    def flush(self):
        if self.last_stmt is not None:
            self.last_stmt.flush()
        self.last_stmt = None
         
class SQLSerializer(object):
    logger = logging.getLogger('fixture.SQLSerializer')

    def __init__(self, out, builder_impl=SQLBuilder, **kwargs):
        self.out = out
        self.builder_impl = builder_impl
        self.kwargs = kwargs

    def __call__(self, suite, digraph):
        builder = self.builder_impl(self.out, **self.kwargs)
        for schema in reversed(digraph.getlist()):
            dataset = suite[schema]
            for data in dataset:
                values = [] 
                for k, v in sorted(data._fields.iteritems(),
                                   lambda a, b: \
                                     -1 if a[0] in data._id_fields \
                                       else (1 if b[0] in data._id_fields \
                                                else cmp(a[0], b[0]))):
                    if isinstance(v, rel):
                        continue
                    elif isinstance(v, Data):
                        if len(v._id_fields) != 1:
                            raise Exception("Number of id fields must be 1 when referring to %s" % v._schema)
                        v = getattr(v, v._id_fields[0])
                    elif isinstance(v, FunctionType):
                        v = v(data)
                    values.append((k, v))
                builder.insert(data._schema, values)
