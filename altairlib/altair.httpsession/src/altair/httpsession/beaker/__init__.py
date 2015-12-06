from __future__ import absolute_import
from ..exceptions import NoSuchSession, SessionAlreadyExists, SessionExpired
from ..api import get_now_from_request
from ..factory import parameters
import datetime
import time

__all__ = [
    'BeakerHTTPSessionBackend',
    'factory',
    ]


class BeakerHTTPSessionBackend(object):
    def __init__(self, now, namespace_manager_factory, timeout=None, backend_always_assumes_timeout_to_be_relative=False, **kwargs):
        self.now = now
        self.timeout = timeout and int(timeout)
        self.namespace_manager_factory = namespace_manager_factory
        self.namespace_manager_factory_args = kwargs
        self.namespace_cache = None
        self.backend_always_assumes_timeout_to_be_relative = backend_always_assumes_timeout_to_be_relative # DAMN!

    def _empty_data(self):
        return {
            '_creation_time': self.now,
            '_accessed_time': self.now,
            }

    @property
    def _expiry(self):
        if self.backend_always_assumes_timeout_to_be_relative:
            return self.timeout
        else:
            if self.timeout is None:
                return None
            return int(self.now + self.timeout)

    def load(self, id_):
        if self.namespace_cache is not None and self.namespace_cache.namespace_cache == id_:
            namespace = self.namespace_cache
        else:
            namespace = self.namespace_cache = self.namespace_manager_factory(namespace=id_, **self.namespace_manager_factory_args)
        data = None
        namespace.acquire_read_lock()
        try:
            try:
                data = namespace['session']
            except KeyError, TypeError:
                pass
            if data is None:
                raise NoSuchSession('No such id: %s' % id_)
        finally:
            namespace.release_read_lock()
        if self.timeout is not None and '_accessed_time' in data and self.now - data['_accessed_time'] >= self.timeout:
            raise SessionExpired('Session expired: %s' % id_)
        return data

    def save(self, id_, data, touch=False):
        if self.namespace_cache is not None and self.namespace_cache.namespace == id_:
            namespace = self.namespace_cache
        else:
            namespace = self.namespace_cache = self.namespace_manager_factory(namespace=id_, **self.namespace_manager_factory_args)
            if 'session' not in namespace or namespace['session'] is None:
                data['_creation_time'] = self.now
        data['_accessed_time'] = self.now

        namespace.acquire_write_lock(replace=True)
        try:
            namespace.set_value('session', data, self._expiry)
        finally:
            namespace.release_write_lock()

    def new(self, id_):
        namespace = self.namespace_cache = self.namespace_manager_factory(namespace=id_, **self.namespace_manager_factory_args)
        namespace.acquire_write_lock(replace=True)
        data = self._empty_data()
        try:
            if 'session' in namespace and namespace['session'] is not None:
                raise SessionAlreadyExists('Session with the same id already exists: %s' % id_)
            namespace.set_value('session', data, self._expiry)
        finally:
            namespace.release_write_lock()
        return data

    def delete(self, id_, data):
        if self.namespace_cache is not None and self.namespace_cache.namespace == id_:
            namespace = self.namespace_cache
        else:
            namespace = self.namespace_cache = self.namespace_manager_factory(namespace=id_, **self.namespace_manager_factory_args)
        namespace.acquire_write_lock(replace=True)
        try:
            del namespace['session']
        except KeyError:
            pass
        finally:
            namespace.release_write_lock()

    def get_creation_time(self, id_, data):
        return data.get('_creation_time', None)

    def get_access_time(self, id_, data):
        return data.get('_accessed_time', None)


@parameters(
    type='str?',
    timeout='float?',
    backend_always_assumes_timeout_to_be_relative='bool?',
    )
def factory(request, type=None, timeout=None, backend_always_assumes_timeout_to_be_relative=None, **kwargs):
    from beaker.cache import clsmap
    now = time.mktime(get_now_from_request(request).timetuple())
    if type is None:
        type = 'memory'
    namespace_manager_factory = clsmap[type]
    if timeout is not None:
        timeout = float(timeout)
    return BeakerHTTPSessionBackend(
        now=now,
        namespace_manager_factory=namespace_manager_factory,
        timeout=timeout,
        backend_always_assumes_timeout_to_be_relative=backend_always_assumes_timeout_to_be_relative,
        **kwargs)
