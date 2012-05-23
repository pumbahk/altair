# -*- coding: utf-8 -*-

from datetime import datetime, date
from decimal import Decimal
import transaction
import json

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, TIMESTAMP
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.sql.expression import text
import sqlalchemy.sql.functions as sqlfunctions
from zope.sqlalchemy import ZopeTransactionExtension
import sqlahelper

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

from paste.util.multidict import MultiDict

def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])

def record_to_multidict(self, filters=dict()):
    app_struct = record_to_appstruct(self)
    def _convert(key, value):
        if value is None:
            return (key, '')
        elif isinstance(value, str) or isinstance(value, unicode) or isinstance(value, int) or isinstance(value, long):
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
            elif isinstance(value, str) \
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
    created_at = Column(TIMESTAMP, nullable=False,
                                   default=datetime.now,
                                   server_default=sqlfunctions.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.now,
                                   server_default=text('0'),
                                   onupdate=datetime.now,
                                   server_onupdate=sqlfunctions.current_timestamp())

class LogicallyDeleted(object):
    deleted_at = Column(TIMESTAMP, nullable=True)

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
    def get(cls, id):
        return cls.filter(cls.id==id).first()

    @classmethod
    def all(cls):
        return cls.filter().all()

    @classmethod
    def clone(cls, origin):
        data = record_to_multidict(origin)
        for column in ['id', 'created_at', 'updated_at', 'deleted_at']:
            if column in data.keys():
                data.pop(column)
        return cls(**data)

    def save(self):
        if hasattr(self, 'id') and self.id:
            self.update()
        else:
            self.add()

    def add(self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        DBSession.add(self)
        DBSession.flush()

    def update(self):
        self.updated_at = datetime.now()
        DBSession.merge(self)
        DBSession.flush()

    def delete(self):
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

    import collections
    from sqlalchemy.ext.mutable import Mutable

class MutationDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutationDict."

        if not isinstance(value, MutationDict):
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
