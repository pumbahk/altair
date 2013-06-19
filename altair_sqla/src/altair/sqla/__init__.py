import itertools

try:
    from sqlalchemy.orm.util import object_state as instance_state
except ImportError:
    from sqlalchemy.orm.attributes import instance_state

try:
    from sqlalchemy.orm.session import _sessions as _all_sessions
except ImportError:
    _all_sessions = None

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

