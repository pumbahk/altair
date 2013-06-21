from sqlalchemy.orm.instrumentation import instance_state
from sqlalchemy.orm.interfaces import MapperProperty, StrategizedProperty
from sqlalchemy.orm.strategies import LazyLoader
from sqlalchemy.orm.attributes import QueryableAttribute, instance_state
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.collections import collection_adapter
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.orm.session import _state_session
import itertools

try:
    from sqlalchemy.orm.util import object_state as instance_state
except ImportError:
    from sqlalchemy.orm.attributes import instance_state

try:
    from sqlalchemy.orm.session import _sessions as _all_sessions
except ImportError:
    _all_sessions = None

__all__ = [
    'association_proxy_many',
    'AssociationProxyMany',
    'get_relationship_clause',
    'property_for',
    'get_strategy',
    'session_partaken_by',
    ]

def _property_for_descriptor(descriptor, configure_mappers=True):
    mapper = class_mapper(descriptor.class_)
    return mapper.get_property(descriptor.key, configure_mappers)

def property_for_descriptor(descriptor, configure_mappers=True):
    if not isinstance(descriptor, QueryableAttribute):
        raise TypeError('descriptor %r is not a QueryableAttribute' % descriptor)
    return _property_for_descriptor(descriptor)

def _property_for(descriptor_property_or_collection, configure_mappers):
    if isinstance(descriptor_property_or_collection, MapperProperty):
        return descriptor_property_or_collection, None
    elif isinstance(descriptor_property_or_collection, QueryableAttribute):
        return _property_for_descriptor(descriptor_property_or_collection, configure_mappers), None
    else:
        adapter = collection_adapter(descriptor_property_or_collection)
        if adapter is None:
            raise TypeError('argument must be any of descriptor, property or instrumented collection, got %r' % descriptor_property_or_collection)
        mapper = class_mapper(adapter.attr.class_)
        return mapper.get_property(adapter.attr.key, configure_mappers), adapter.owner_state

def property_for(descriptor_property_or_collection, configure_mappers=True):
    return _property_for(descriptor_property_or_collection, configure_mappers)[0]

def get_strategy(property, cls):
    if not isinstance(property, StrategizedProperty):
        raise TypeError('%r is not a StrategizedProperty' % cls)
    return property._get_strategy(cls)

def get_relationship_clause(descriptor_property_or_collection, state_or_object=None):
    property, state = _property_for(descriptor_property_or_collection, True)
    if not isinstance(property, RelationshipProperty):
        raise TypeError('Cannot retrieve relationship property from %r' % descriptor_property_or_collection)

    if state_or_object is None and state is None:
        raise TypeError('Could not extract instance state from %r' % descriptor_property_or_collection)
    elif state is None:
        if isinstance(state_or_object, InstanceState):
            state = state_or_object
        else:
            state = instance_state(state_or_object)

    return get_strategy(property, LazyLoader).lazy_clause(state)

def get_relationship_query(descriptor_property_or_collection, state_or_object=None):
    property, state = _property_for(descriptor_property_or_collection, True)
    if not isinstance(property, RelationshipProperty):
        raise TypeError('Cannot retrieve relationship property from %r' % descriptor_property_or_collection)

    if state_or_object is None and state is None:
        raise TypeError('Could not extract instance state from %r' % descriptor_property_or_collection)
    elif state is None:
        if isinstance(state_or_object, InstanceState):
            state = state_or_object
        else:
            state = instance_state(state_or_object)

    strategy = get_strategy(property, LazyLoader)

    mapper = strategy.mapper
    session = _state_session(state)
    return session.query(mapper).filter(strategy.lazy_clause(state))

def association_proxy_many(target_name, attr_name):
    return AssociationProxyMany(target_name, attr_name)

class AssociationProxyMany(object):
    def __init__(self, target_name, attr_name, collection_type=list):
        self.target_name = target_name
        self.attr_name = attr_name
        self.collection_type = collection_type

    def __get__(self, obj, class_):
        target = getattr(obj, self.target_name)
        return self.collection_type(itertools.chain(*[getattr(t, self.attr_name)
                                                      for t in target]))

def session_partaken_by(obj):
    state = instance_state(obj) 
    if hasattr(state, 'session'):
        session = state.session
    else:
        assert hasattr(state, 'session_id') and _all_sessions is not None
        session = _all_sessions[state.session_id]
    return session

