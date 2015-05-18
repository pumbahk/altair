import mock
from datetime import datetime
import json
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.sql.operators import ColumnOperators
import logging

logger = logging.getLogger()
Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class ForDisplayByHelperMixin(object):
    def __int__(self):
        return 0

    def weekday(self): #for datetime
        return 0

    def encode(self, *args, **kwargs):
        return repr(self)

    def decode(self, *args, **kwargs):
        return repr(self).decode(*args, **kwargs)

    def __radd__(self, x):
        return x + repr(self)

class QuietMock(ForDisplayByHelperMixin, mock.Mock):
    _m_message = u"-"
    def __repr__(self):
        return self._m_message

    def __iter__(self):
        return iter([])

    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

def null_model(model): #xxx:
    m = QuietMock("Null{}".format(model.__name__))
    m.mock_add_spec(model)
    # if hasattr(m,  "id"):
    #     m.id = -1
    return m

def first_or_nullmodel(parent, relation_name):
    children = getattr(parent, relation_name)
    try:
        return children[0]
    except IndexError as e:
        logger.warn("first_or_nullmodel %s:%s -- %s", parent, relation_name, repr(e))
        child_class = getattr(parent.__class__, relation_name).property.mapper.class_
        return null_model(child_class)

def model_to_dict(obj):
    return {k: getattr(obj, k) for k, v in obj.__class__.__dict__.iteritems() \
                if isinstance(v, ColumnOperators)}

def model_from_dict(modelclass, D):
    instance = modelclass()
    items_fn = D.iteritems if hasattr(D, "iteritems") else D.items
    trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date = None, None, None, None
    for k, v in items_fn():
        if v:
            if k == "trackingcode_parts":
                trackingcode_parts = v
            elif k == "trackingcode_genre":
                trackingcode_genre = v
            elif k == "trackingcode_eventcode":
                trackingcode_eventcode = v
            elif k == "trackingcode_date":
                trackingcode_date = v
            else:
                try:
                    setattr(instance, k, v)
                except Exception as e:
                    logger.warn("class=%s, k=%s, v=%s, message=%s", modelclass, k, v, e)
    if None not in [trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date]:
        instance.trackingcode = "_".join([trackingcode_parts, trackingcode_genre, trackingcode_eventcode, trackingcode_date.strftime("%Y%m%d")])
    return instance

def model_column_items(obj):
    return [(k, v) for k, v in obj.__class__.__dict__.items()\
                if isinstance(v, ColumnOperators)]

def model_column_iters(modelclass, D):
    for k, v in modelclass.__dict__.items():
        if isinstance(v, ColumnOperators):
            yield k, D.get(k)

def model_clone(obj):
    cls = obj.__class__
    cloned = cls()
    pk_keys = set([c.key for c in orm.class_mapper(cls).primary_key])
    for p in  orm.class_mapper(cls).iterate_properties:
        if p.key not in  pk_keys:
            setattr(cloned, p.key, getattr(obj, p.key, None))
    return cloned

class BaseOriginalMixin(object):
    def __copy__(self):
        copied = model_clone(self)
        now = datetime.now()
        if hasattr(copied, "created_at"):
            copied.created_at = now
        if hasattr(copied, "updated_at"):
            copied.updated_at = now
        return copied

    def to_dict(self):
        return model_to_dict(self)

    def column_items(self):
        return model_column_items(self)

    @classmethod
    def column_iters(cls, D):
        return model_column_iters(cls, D)

    @classmethod
    def from_dict(cls, D):
        return model_from_dict(cls, D)

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

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        self.changed()
