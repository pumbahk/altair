from datetime import datetime
import sqlahelper
import json
from sqlalchemy import (
    Column,
)
from sqlalchemy.types import (
    Integer,
    BigInteger,
    TIMESTAMP,
    VARCHAR,
    TypeDecorator,
    Unicode,
)
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import (
    deferred,
)
from sqlalchemy.ext.declarative import declared_attr
from .nervous import NervousJSONDecoder, NervousDict, NervousList

class Identifier(Integer):
    def __init__(self, *args, **kwargs):
        self._inner = None
        self._args = args
        self._kwargs = kwargs

    def _compiler_dispatch(self, visitor, **kw):
        return self.inner._compiler_dispatch(visitor, **kw)

    @property
    def inner(self):
        if self._inner is None:
            type_ = BigInteger
            try:
                if sqlahelper.get_engine().dialect.name == 'sqlite':
                    type_ = Integer
            except:
                pass
            self._inner = type_(*self._args, **self._kwargs)
        return self._inner

    def get_dbapi_type(self, dbapi):
        return self.inner.get_dbapi_type(dbapi)

    @property
    def python_type(self):
        return self.inner.python_type

    @property
    def _expression_adaptations(self):
        return self.inner._expression_adaptations

class WithCreatedAt(object):
    __clone_excluded__ = ['created_at']

    @declared_attr
    def created_at(self):
        return deferred(Column(TIMESTAMP, nullable=False,
                               default=datetime.now,
                               server_default=sqlf.current_timestamp()))


class WithTimestamp(WithCreatedAt):
    __clone_excluded__ = WithCreatedAt.__clone_excluded__ + ['updated_at']

    @declared_attr
    def updated_at(self):
        return deferred(Column(TIMESTAMP, nullable=False,
                               default=datetime.now,
                               server_default=text('0'),
                               onupdate=datetime.now,
                               server_onupdate=sqlf.current_timestamp()))

class LogicallyDeleted(object):
    __clone_excluded__ = ['deleted_at']

    @declared_attr
    def deleted_at(self):
        return deferred(Column(TIMESTAMP, nullable=True, index=True))


class JSONEncodedObject(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = NervousJSONDecoder().decode(value)
        return value

JSONEncodedDict = JSONEncodedObject # B/C

class MutationJSONObjectBase(Mutable):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutationDict."

        if isinstance(value, basestring):
            json_obj = NervousJSONDecoder(dict_class=MutationDict, list_class=MutationList).decode(value)
        elif not isinstance(value, MutationJSONObjectBase):
            if isinstance(value, dict):
                json_obj = MutationDict(value)
            elif isinstance(value, (list, tuple)):
                json_obj = MutationList(value)
            else:
                return Mutable.coerce(key, value)
        else:
            return value
        return json_obj

class MutationDict(MutationJSONObjectBase, NervousDict):
    def _changed(self, modified):
        self.changed()

class MutationList(MutationJSONObjectBase, NervousList):
    def _changed(self, modified):
        self.changed()


class SpaceDelimitedList(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return u' '.join(unicode(v).strip() for v in value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            s = value.strip(u' ')
            if not s:
                return []
            else:
                return s.split(u' ')


class MutableSpaceDelimitedList(Mutable, NervousList):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableSpaceDelimitedList):
            try:
                i = iter(value)
            except TypeError:
                return Mutable.coerce(key, value)
            return MutableSpaceDelimitedList(i)
        else:
            return value

    def _changed(self, modified):
        self.changed()
