# -*- coding: utf-8 -*-

from datetime import datetime, date, time
from decimal import Decimal
import json

from sqlalchemy import Table, Column, ForeignKey, ForeignKeyConstraint, Index, func
from sqlalchemy.orm import column_property, scoped_session, deferred, relationship as _relationship
from sqlalchemy.orm.attributes import manager_of_class, QueryableAttribute
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql.expression import text, desc, asc
from sqlalchemy.sql import functions as sqlf, and_
import sqlahelper
from paste.util.multidict import MultiDict
from altair.sqla import get_relationship_query

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

from altair.models import Identifier, WithTimestamp, LogicallyDeleted, JSONEncodedDict, MutationDict

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

def merge_session_with_post(session, post, filters={}, excludes=set()):
    def _set_attrs(session, values):
        for key,value in values:
            if key in excludes:
                continue
            filter = filters.get(key)
            try:
                if filter is not None:
                    value = filter(session, value)
                    setattr(session, key, value)
                elif isinstance(value, str)\
                    or isinstance(value, unicode)\
                    or isinstance(value, int)\
                    or isinstance(value, long)\
                    or isinstance(value, Decimal)\
                    or isinstance(value, datetime)\
                    or isinstance(value, date)\
                    or isinstance(value, time)\
                    or value is None:
                    setattr(session, key, value)
                else:
                    pass
            except AttributeError:
                raise AttributeError("can't set attribute \"%s\"" % key)

    if type(post) is list:
        _set_attrs(session, post)
        return session
    elif type(post) is dict:
        _set_attrs(session, post.items())
        return session
    else:
        raise Exception(u'Invalid post type type= %s' % type(post))

def _flush_or_rollback():
    try:
        DBSession.flush()
    except:
        DBSession.rollback()
        raise

def add_and_flush(session):
    DBSession.add(session)
    _flush_or_rollback()

def merge_and_flush(session):
    DBSession.merge(session)
    _flush_or_rollback()

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
            raise TypeError("No mapper is defined for %s" % cls)

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
                    if objs:
                        setattr(retval, key, objs)
                else:
                    obj = getattr(origin, key)
                    if obj:
                        setattr(retval, key, self(obj.__class__, obj))

        return retval

class BaseModel(object):
    __clone_excluded__ = ['id']

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
            if not self.created_at:
                self.created_at = datetime.now()
            self.updated_at = datetime.now()
        DBSession.add(self)
        _flush_or_rollback()

    def update(self):
        if isinstance(self, WithTimestamp):
            self.updated_at = datetime.now()
        DBSession.merge(self)
        _flush_or_rollback()

    def delete(self):
        if isinstance(self, LogicallyDeleted):
            self.deleted_at = datetime.now()
        DBSession.merge(self)
        _flush_or_rollback()

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

class DomainConstraintError(Exception):
    pass

def is_any_of(item, collection):
    if isinstance(item, QueryableAttribute):
        return item.in_(collection)
    else:
        return item in collection

def asc_or_desc(query, column, direction, default=None):
    fn = dict(desc=desc, asc=asc).get(direction or default)
    if fn is not None:
        query = query.order_by(fn(column))
    return query

class HyphenationCodecMixin(object):
    _encoder = unicode
    _decoder = long

    def decoder(self, value):
        return [self._decoder(v) for v in value.split('-')] if value is not None else None

    def encoder(self, value):
        return u'-'.join(self._encoder(v) for v in value) if value is not None else None

class CollectionModelBase(object):
    def __init__(self, relationship, label_builder, id_keys):
        self.relationship = relationship
        self.label_builder = label_builder
        self.id_keys = id_keys

    def __len__(self):
        return len(self.relationship)

    def __contains__(self, value):
        return value in self.relationship

    def __iter__(self):
        if callable(self.id_keys):
            for item in self.relationship:
                key = self.id_keys(self, item)
                yield self.encoder(key), key, self.label_builder(self, item)
        else:
            for item in self.relationship:
                key = tuple(getattr(item, key) for key in self.id_keys)
                yield self.encoder(key), key, self.label_builder(self, item)

class GroupedCollectionModelBase(object):
    def __init__(self, relationship, label_builder, id_keys):
        self.relationship = relationship
        self.label_builder = label_builder
        self.id_keys = id_keys

    def __len__(self):
        return len(self.relationship)

    def __contains__(self, value):
        return value in self.relationship

    def __iter__(self):
        if callable(self.id_keys):
            def iter_inner(group_name, items):
                for item in items:
                    key = self.id_keys(self, item)
                    yield self.encoder(key), key, self.label_builder(self, (group_name, item))
        else:
            def iter_inner(group_name, items):
                for item in items:
                    key = tuple(getattr(item, key) for key in self.id_keys)
                    yield self.encoder(key), key, self.label_builder(self, (group_name, item))

        for group_name, items in self.relationship:
            yield group_name, iter_inner(group_name, items)

class HyphenatedCollectionModel(CollectionModelBase, HyphenationCodecMixin):
    pass

class HyphenatedGroupedCollectionModel(GroupedCollectionModelBase, HyphenationCodecMixin):
    pass
