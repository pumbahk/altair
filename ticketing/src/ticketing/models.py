# -*- coding: utf-8 -*-

from datetime import datetime, date
import transaction

from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import IntegrityError
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
    status = Column(Integer, default=1)

    @classmethod
    def get(cls, id):
        return DBSession.query(cls).filter(cls.id==id).first()

    @classmethod
    def all(cls):
        return DBSession.query(cls).filter(cls.deleted_at==None).all()

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
