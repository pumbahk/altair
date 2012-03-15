# -*- coding: utf-8 -*-

import transaction

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.exc import IntegrityError
from zope.sqlalchemy import ZopeTransactionExtension
import sqlahelper

print "boxoffice"
Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

from paste.util.multidict import MultiDict
from .boxoffice import *

def record_to_appstruct(self):
    return dict([(k, self.__dict__[k]) for k in sorted(self.__dict__) if '_sa_' != k[:4]])

def record_to_multidict(self):
    appstruct = record_to_appstruct(self)
    return MultiDict(appstruct.items())

import datetime
def merge_session_with_post(session, post, filters={}):
    def _set_attrs(session, values):
        for key,value in values:
            filter = filters.get(key)
            if filter is not None:
                value = filter(session, value)
                setattr(session, key, value)
            elif isinstance(value, str) \
                or isinstance(value, unicode) \
                or isinstance(value, datetime.datetime) \
                or isinstance(value, datetime.date):
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