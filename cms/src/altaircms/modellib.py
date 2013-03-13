import json
import sqlahelper
import sqlalchemy.orm as orm
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.sql.operators import ColumnOperators
    
Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

def model_to_dict(obj):
    return {k: getattr(obj, k) for k, v in obj.__class__.__dict__.iteritems() \
                if isinstance(v, ColumnOperators)}

def model_from_dict(modelclass, D):
    instance = modelclass()
    items_fn = D.iteritems if hasattr(D, "iteritems") else D.items
    for k, v in items_fn():
        setattr(instance, k, v)
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
