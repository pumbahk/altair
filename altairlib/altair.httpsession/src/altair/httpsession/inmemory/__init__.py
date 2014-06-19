from __future__ import absolute_import
from ..exceptions import NoSuchSession, SessionAlreadyExists, SessionExpired
from ..api import get_now_from_request
from ..utils import asbool
from ..factory import parameters
import datetime
import pickle
import time

__all__ = [
    'InMemoryHTTPSessionBackend',
    'factory',
    ]


class PickleMarshal(object):
    def __init__(self):
        pass

    def dumps(self, data):
        return pickle.dumps(data)

    def loads(self, payload):
        return pickle.loads(payload)


class InMemoryHTTPSessionBackend(object):
    def __init__(self, now, store, marshal=PickleMarshal(), timeout=None, **kwargs):
        self.now = now
        self.store = store
        self.marshal = marshal
        self.timeout = timeout and int(timeout)

    def _empty_data(self):
        return {
            '_creation_time': self.now,
            '_accessed_time': self.now,
            }

    def _dumps(self, data):
        return self.marshal.dumps(data)

    def _loads(self, payload):
        return self.marshal.loads(payload)

    def load(self, id_):
        payload = self.store.get(id_)
        if payload is None:
            raise NoSuchSession()
        data = self._loads(payload)
        if self.timeout is not None and '_accessed_time' in data and self.now - data['_accessed_time'] >= self.timeout:
            raise SessionExpired('Session expired: %s' % id_)
        return data

    def save(self, id_, data, touch=False):
        data['_accessed_time'] = self.now
        payload = self._dumps(data)
        self.store[id_] = payload

    def new(self, id_):
        data = self._empty_data()
        payload = self._dumps(data)
        if id_ in self.store:
            raise SessionAlreadyExists('Session with the same id already exists: %s' % id_)
        self.store[id_] = payload
        return data

    def delete(self, id_, data):
        try:
            del self.store[id_]
        except KeyError:
            pass

    def get_creation_time(self, id_, data):
        return data.get('_creation_time', None)

    def get_access_time(self, id_, data):
        return data.get('_accessed_time', None)


stores = {}

@parameters(
    store_name='str?',
    )
def factory(request, store_name='default', **kwargs):
    now = time.mktime(get_now_from_request(request).timetuple())
    store = stores.setdefault(store_name, {})
    return InMemoryHTTPSessionBackend(
        now=now,
        store=store,
        **kwargs)

