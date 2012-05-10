# -*- coding: utf-8 -*-

from datetime import datetime, date
import transaction

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import TypeDecorator, VARCHAR
import json
from zope.sqlalchemy import ZopeTransactionExtension
import collections
from sqlalchemy.ext.mutable import Mutable
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
        elif isinstance(value, str) or isinstance(value, unicode):
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
                or isinstance(value, datetime) \
                or isinstance(value, date):
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

class BaseModel(object):
    created_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    @classmethod
    def get(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()

    @classmethod
    def all(cls):
        return DBSession.query(cls).filter(cls.deleted_at==None).all()

    @classmethod
    def find_by(cls, **conditions):
        return DBSession.query(cls).filter_by(**conditions).all()

    def save(self):
        if self.id:
            self.updated_at = datetime.now()
            DBSession.merge(self)
        else:
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            DBSession.add(self)
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