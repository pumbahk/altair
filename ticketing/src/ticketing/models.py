# -*- coding: utf-8 -*-

from datetime import datetime, date
from decimal import Decimal
from math import floor
import isodate
import transaction
import json

from sqlalchemy import Table, Column, ForeignKey, ForeignKeyConstraint, Index, func
from sqlalchemy.types import TypeEngine, TypeDecorator, VARCHAR, BigInteger, Integer, String, TIMESTAMP
from sqlalchemy.orm import column_property, scoped_session, deferred, relationship as _relationship
from sqlalchemy.orm.attributes import manager_of_class
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf, and_
from zope.sqlalchemy import ZopeTransactionExtension
import sqlahelper
from paste.util.multidict import MultiDict

from ticketing.utils import StandardEnum

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

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
            self._inner = (BigInteger if sqlahelper.get_engine().dialect.name != 'sqlite' else Integer)(*self._args, **self._kwargs)
        return self._inner

    def get_dbapi_type(self, dbapi):
        return self.inner.get_dbapi_type(dbapi)

    @property
    def python_type(self):
        return self.inner.python_type

    @property
    def _expression_adaptations(self):
        return self.inner._expression_adaptations

def record_to_appstruct(obj):
    manager = manager_of_class(type(obj))
    if manager is None:
        raise TypeError("No mapper is defined for %s" % type(obj))
    keys = []
    for property in manager.mapper.iterate_properties:
        if isinstance(property, ColumnProperty):
            keys.append(property.key)

    return dict((k, getattr(obj, k, None)) for k in keys)

def record_to_multidict(self, filters=dict()):
    app_struct = record_to_appstruct(self)
    def _convert(key, value):
        if value is None:
            return (key, '')
        elif isinstance(value, str)\
             or isinstance(value, unicode)\
             or isinstance(value, int)\
             or isinstance(value, long)\
             or isinstance(value, MutationDict):
            return (key, value)
        elif isinstance(value, date) or isinstance(value, datetime):
            filter = filters.get(key)
            return (key, (filter(value) if filter else str(value)))
        else:
            return (key, str(value))

    return MultiDict([ _convert (k, v) for k,v in app_struct.items()])

def merge_session_with_post(session, post, filters={}):
    def _set_attrs(session, values):
        for key,value in values:
            filter = filters.get(key)

            if filter is not None:
                value = filter(session, value)
                setattr(session, key, value)
            elif isinstance(value, str)\
                or isinstance(value, unicode)\
                or isinstance(value, int)\
                or isinstance(value, Decimal)\
                or isinstance(value, datetime)\
                or isinstance(value, date)\
                or value is None:
                setattr(session, key, value)
            else:
                pass

    if type(post) is list:
        _set_attrs(session, post)
        return session
    elif type(post) is dict:
        _set_attrs(session, post.items())
        return session
    else:
        raise Exception(u'Invalid post type type= %s' % type(post))

def add_and_flush(session):
    DBSession.add(session)
    DBSession.flush()

def merge_and_flush(session):
    DBSession.merge(session)
    DBSession.flush()

class WithTimestamp(object):
    __clone_excluded__ = ['created_at', 'updated_at']

    @declared_attr
    def created_at(self):
        return deferred(Column(TIMESTAMP, nullable=False,
                               default=datetime.now,
                               server_default=sqlf.current_timestamp()))
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


class Cloner(object):
    def __init__(self, deep):
        self.deep = deep
        self.visited = {}

    def __call__(self, cls, origin, excluded=None):
        if not issubclass(type(origin), cls):
            raise TypeError("%s is not a subclass of %s" % (type(origin), cls))
        retval = self.visited.get(origin)
        if retval is not None:
            return retval

        excluded_properties = set()
        for super_cls in cls.__mro__:
            excluded_ = getattr(super_cls, '__clone_excluded__', None)
            if excluded_ is not None:
                excluded_properties.update(excluded_)
        if excluded is not None:
            excluded_properties.update(excluded)

        manager = manager_of_class(cls)
        if manager is None:
            raise TypeError("No mapper is defined for %s" % type(obj))

        columns = {}
        relationships = {}
        for property in manager.mapper.iterate_properties:
            if isinstance(property, ColumnProperty):
                columns[property.key] = property
            if isinstance(property, RelationshipProperty):
                relationships[property.key] = property

        retval = cls()
        self.visited[origin] = retval

        for key, property in columns.iteritems():
            if key in excluded_properties:
                continue
            setattr(retval, key, getattr(origin, key)) 

        if self.deep:
            for key, property in relationships.iteritems():
                if key in excluded_properties:
                    continue
                if property.uselist:
                    objs = []
                    for obj in getattr(origin, key):
                        if not hasattr(obj.__class__, 'clone'):
                            raise TypeError('%s, contained in property %s is not cloneable' % (obj, key))
                        objs.append(self(obj.__class__, obj))
                    setattr(retval, key, objs)
                else:
                    obj = getattr(origin, key)
                    setattr(retval, key, self(obj.__class__, obj))

        return retval

class BaseModel(object):
    query = DBSession.query_property()

    @classmethod
    def filter(cls, expr=None):
        q = cls.query
        if hasattr(cls, 'deleted_at'):
            q = q.filter(cls.deleted_at==None)
        if expr is not None:
            q = q.filter(expr)
        return q

    @classmethod
    def filter_by(cls, **conditions):
        return cls.filter().filter_by(**conditions)

    @classmethod
    def get(cls, id=None, **kwargs):
        if id is not None:
            kwargs['id'] = id
        return cls.filter_by(**kwargs).first()

    @classmethod
    def all(cls):
        return cls.filter().all()

    @classmethod
    def clone(cls, origin, deep=False, excluded=None):
        return Cloner(deep)(cls, origin, excluded)

    def save(self):
        if hasattr(self, 'id') and self.id:
            self.update()
        else:
            self.add()

    def add(self):
        if hasattr(self, 'id') and not self.id:
            del self.id
        if isinstance(self, WithTimestamp):
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
        DBSession.add(self)
        DBSession.flush()

    def update(self):
        if isinstance(self, WithTimestamp):
            self.updated_at = datetime.now()
        DBSession.merge(self)
        DBSession.flush()

    def delete(self):
        if isinstance(self, LogicallyDeleted):
            self.deleted_at = datetime.now()
        DBSession.merge(self)
        DBSession.flush()

class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class MutationDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutationDict."

        if isinstance(value, basestring):
            return MutationDict(json.loads(value))   
        elif not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)

            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."

        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."

        dict.__delitem__(self, key)
        self.changed()

class CustomizedRelationshipProperty(RelationshipProperty):
    def _determine_joins(self):
        RelationshipProperty._determine_joins(self)

        # secondary joinがある場合はdeleted_at条件の自動付加は行わない
        if hasattr(self, 'secondary') and self.secondary is not None:
            return

        # primary joinに論理削除レコードを対象外とする条件を自動付加する
        for column in self.parent.mapped_table.columns:
            if column.name == 'deleted_at':
                self.primaryjoin = and_(self.primaryjoin, column==None)
                break
        for column in self.target.columns:
            if column.name == 'deleted_at':
                self.primaryjoin = and_(self.primaryjoin, column==None)
                break

relationship = _relationship
#def relationship(argument, secondary=None, **kwargs):
#    return CustomizedRelationshipProperty(argument, secondary=secondary, **kwargs)


