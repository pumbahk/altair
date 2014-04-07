from __future__ import absolute_import
from ..exceptions import NoSuchSession, SessionAlreadyExists, SessionExpired
from ..api import get_now_from_request
from ..utils import asbool
from ..factory import parameters
from redis import StrictRedis
import pickle
import datetime
import time

__all__ = [
    'RedisHTTPSessionBackend',
    'factory',
    ]


class PickleMarshal(object):
    def __init__(self):
        pass

    def dumps(self, data):
        return pickle.dumps(data)

    def loads(self, payload):
        return pickle.loads(payload)


class RedisHTTPSessionBackend(object):
    def __init__(self, now, redis, marshal=PickleMarshal(), key_modifier=lambda k:k, timeout=None, **kwargs):
        self.now = now
        self.redis = redis
        self.marshal = marshal
        self.key_modifier = key_modifier
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
        modified_key = self.key_modifier(id_)
        payload = self.redis.get(modified_key)
        if payload is None:
            raise NoSuchSession()
        data = self._loads(payload)
        if self.timeout is not None and '_accessed_time' in data and self.now - data['_accessed_time'] >= self.timeout:
            raise SessionExpired('Session expired: %s' % id_)
        return data

    def save(self, id_, data, touch=False):
        modified_key = self.key_modifier(id_)
        data['_accessed_time'] = self.now
        payload = self._dumps(data)
        if self.timeout is None:
            self.redis.set(modified_key, payload)
        else:
            self.redis.setex(modified_key, self.timeout, payload)

    def new(self, id_):
        modified_key = self.key_modifier(id_)
        data = self._empty_data()
        payload = self._dumps(data)
        # SETNXEX is exactly what we want
        if self.redis.setnx(modified_key, payload) == 0:
            raise SessionAlreadyExists('Session with the same id already exists: %s' % id_)
        if self.timeout is not None:
            self.redis.expire(modified_key, self.timeout)
        return data

    def delete(self, id_, data):
        modified_key = self.key_modifier(id_)
        self.redis.delete(modified_key)

    def get_creation_time(self, id_, data):
        return data.get('_creation_time', None)

    def get_access_time(self, id_, data):
        return data.get('_accessed_time', None)


@parameters(
    host='str?',
    port='int?',
    db='int?',
    password='str?',
    socket_timeout='float?',
    unix_socket_path='str?',
    url='str?',
    timeout='int?',
    connection_pool='class',
    marshal='instance',
    key_modifier='callable',
    )
def factory(request, host='localhost', port=6379, db=0, password=None, socket_timeout=None, unix_socket_path=None, url=None, timeout=None, connection_pool=None, **kwargs):
    now = time.mktime(get_now_from_request(request).timetuple())
    redis_py_url = False
    if url is not None:
        if url.startswith('redis:'):
            redis_py_url = True
        else:
            # beaker_extension compatibility
            host_port_pair, _, params = url.partition('?') 
            host, _, port_ = host_port_pair.partition(':')
            if port_:
                port = int(port_)
            if params:
                extra_params = dict(tuple(urllib.unquote(c) for c in pair.split('=', 1)) for pair in params.split('&'))
                db_ = extra_params.get('db')
                if db is not None:
                    db = db_
                password_ = extra_params.get('password')
                if password is not None:
                    password = password_
                socket_timeout_ = extra_params.get('socket_timeout')
                if socket_timeout is not None:
                    socket_timeout = socket_timeout_
                unix_socket_path_ = extra_params.get('unix_socket_path')
                if unix_socket_path is not None:
                    unix_socket_path = unix_socket_path_
    if redis_py_url:
        redis = StrictRedis.from_url(
            url,
            socket_timeout=socket_timeout,
            connection_pool=connection_pool
            )
    else:
        redis = StrictRedis(
            host=host,
            port=port,
            db=db,
            password=password,
            unix_socket_path=unix_socket_path,
            socket_timeout=socket_timeout,
            connection_pool=connection_pool
            )
    return RedisHTTPSessionBackend(
        now=now,
        redis=redis,
        timeout=timeout,
        **kwargs)
