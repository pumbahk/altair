# -*- coding: utf-8 -*-

import transaction

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import IntegrityError
from zope.sqlalchemy import ZopeTransactionExtension
import sqlahelper

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

from .boxoffice import *

def populate():
    pass

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()
    return DBSession


def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])

def merge_session_with_post(session, post, filters={}):
    def _set_attrs(session, values):
        for key,value in values:
            attr = getattr(session, key)
            filter = filters.get(key)
            if filter is not None:
                value = filter(value)
            setattr(session, key, value)
                
    if type(post) is list:
        _set_attrs(session, post)
        return session
    elif type(post) is dict:
        _set_attrs(session, post.items())
        return session
    else:
        raise Exception('Invalid post type type= %s' % type(post))



def merge_and_flush(session):
    DBSession.merge(session)
    DBSession.flush()