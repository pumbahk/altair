import warnings
import datetime
import time

from .exceptions import *
from .cookies import PlainCookie, SignedCookie
from .factory import parameters
from pytz import UTC

__all__ = [
    'HTTPSession',
    'CookieSessionBinder',
    'BasicHTTPSessionManager',
    'DummyHTTPBackend',
    'get_now_from_request',
    ]

def get_now_from_request(request):
    now = getattr(request, 'current_time', None)
    if now is None:
        now = datetime.datetime.now()
    else:
        if isinstance(now, float):
            now = datetime.datetime.fromtimestamp(now)
        elif not isinstance(now, datetime.datetime):
            raise TypeError('type(self.now) expected to be either a float or datetime.datetime instance, got %r' % now)
    return now


class HTTPSession(object):
    def __init__(self, context, id_=None):
        self.context = context
        self._id = id_
        self.dirty = False
        self._data = None
        self.original_dict = None
        self.is_new = True
        if id_ is not None:
            try:
                self.load()
                self.is_new = False
            except:
                self._id = None

    @property
    def id(self):
        self._populate_data()
        return self._id

    def delete(self):
        if self._id is not None:
            old_id = self._id
            old_data = self._data
            self.context.persistence_backend.delete(self._id, self._data)
            self._id = None
            self._data = None
            self.dirty = False
            self.is_new = True
            self.context.on_delete(old_id, old_data)

    def refresh(self):
        if self._id is not None:
            old_id = self._id
            old_data = self._data
            self.context.persistence_backend.delete(self._id, self._data)
            self.context.on_delete(old_id, old_data)
            self.context.persistence_backend.save(self._id, self._data, False)
            self.dirty = False
            self.is_new = False
            self.context.on_save(self._id, self._data)

    def invalidate(self):
        self.delete()
        self._populate_data()

    def save(self):
        self._populate_data()
        self.context.persistence_backend.save(self._id, self._data, not self.dirty)
        self.dirty = False
        self.is_new = False
        self.context.on_save(self._id, self._data)

    def persist(self):
        self.save()

    def load(self):
        if self._id is not None:
            self._data = self.context.persistence_backend.load(self._id)
            self.dirty = False
            self.is_new = False
            self.original_dict = self._data.copy()
            self.context.on_load(self._id, self._data)

    def revert(self):
        self._data = self.original_dict
        self.dirty = True

    def _populate_data(self):
        if self._id is None:
            new_id = self.context.generate_id()
            self._data = self.context.persistence_backend.new(new_id)
            self._id = new_id
            self.original_dict = {}
            self.context.on_new(self._id, self._data)

    def items(self):
        self._populate_data()
        return self._data.items()

    def iteritems(self):
        return self.items()

    def keys(self):
        self._populate_data()
        return self._data.keys()

    def iterkeys(self):
        return self.keys()

    def values(self):
        self._populate_data()
        return self._data.values()

    def itervalues(self):
        return self.values()

    def setdefault(self, key, value):
        self._populate_data()
        if key not in self._data:
            self.dirty = True
            self._data[key] = value
            return value
        else:
            return self._data[key]

    def pop(self, key, *args):
        if len(args) >= 2:
            raise TypeError('pop expects at most 2 arguments, got %d' % (len(args) + 1))
        self._populate_data()
        try:
            retval = self._data.pop(key)
            self.dirty = True
        except KeyError:
            if args:
                retval = args[0]
            else:
                raise
        return retval

    def get(self, key, default=None):
        self._populate_data()
        return self._data.get(key, default)

    def popitem(self):
        self._populate_data()
        self.dirty = True
        return self._data.popitem()

    def __getitem__(self, key):
        self._populate_data()
        return self._data[key]

    def __setitem__(self, key, value):
        self._populate_data()
        self.dirty = True
        self._data[key] = value

    def __delitem__(self, key):
        self._populate_data()
        del self._data[key]
        self.dirty = True

    def __contains__(self, key):
        self._populate_data()
        return key in self._data

    def __len__(self):
        self._populate_data()
        return len(self._data)

    def __iter__(self):
        self._populate_data()
        return iter(self._data)

    @property
    def created(self):
        self._populate_data()
        return self.context.persistence_backend.get_creation_time(self._id, self._data)

    @property
    def accessed(self):
        self._populate_data()
        return self.context.persistence_backend.get_access_time(self._id, self._data)


class HTTPSessionContext(object):
    def __init__(self, persistence_backend, http_backend, id_generator):
        self.persistence_backend = persistence_backend
        self.http_backend = http_backend
        self.id_generator = id_generator

    def on_load(self, id_, data):
        self.http_backend.bind(id_)

    def on_new(self, id_, data):
        self.http_backend.bind(id_)

    def on_save(self, id_, data):
        pass

    def on_delete(self, id_, data):
        self.http_backend.unbind(id_)

    def generate_id(self):
        return self.id_generator()


class DummyHTTPBackend(object):
    def bind(self, id_):
        pass

    def unbind(self, id_):
        pass

    def get(self):
        return None

    def modify_response(self, resp):
        pass


@parameters(
    cookie='str',
    key='str?',
    cookie_expires='timedelta?',
    cookie_domain='str?',
    cookie_path='str?',
    secure='bool?',
    httponly='bool?'
    )
class CookieSessionBinder(object):
    def __init__(self, cookie, key='beaker.session.id', cookie_expires=None, cookie_domain=None, cookie_path='/', secure=False, httponly=False, now=None, **kwargs):
        self.key = str(key)
        self.cookie_expires = cookie_expires
        self.cookie_domain = cookie_domain
        self.cookie_path = cookie_path
        self.secure = secure
        self.httponly = httponly
        self.cookie = cookie
        if now is None:
            now = datetime.datetime.utcnow()
        else:
            if now.tzinfo is not None:
                now = now.astimezone(UTC)
        self.now = now

    def _set_cookie(self, id_, expires):
        self.cookie[self.key] = id_
        if self.cookie_domain:
            self.cookie[self.key]['domain'] = self.cookie_domain
        if self.secure:
            self.cookie[self.key]['secure'] = True
        if self.cookie_path:
            self.cookie[self.key]['path'] = self.cookie_path
        if expires is not None:
            self.cookie[self.key]['expires'] = expires.strftime("%a, %d-%b-%Y %H:%M:%S GMT")
        if self.httponly:
            try:
                self.cookie[self.key]['httponly'] = True
            except Cookie.CookieError as e:
                if 'Invalid Attribute httponly' not in str(e):
                    raise
                warnings.warn('Python 2.6+ is required to use httponly')

    def bind(self, id_):
        expires = None
        if self.cookie_expires is not None:
            if self.cookie_expires is False:
                expires = datetime.datetime.utcfromtimestamp(0x7fffffff)
            elif isinstance(self.cookie_expires, datetime.timedelta):
                expires = self.now + self.cookie_expires
            elif isinstance(self.cookie_expires, datetime.datetime):
                expires = self.cookie_expires
        return self._set_cookie(id_, expires)

    def unbind(self, id_):
        self._set_cookie(id_, self.now - datetime.timedelta(365))

    def get(self):
        if self.key in self.cookie:
            return self.cookie[self.key].value
        else:
            return None 

    def modify_response(self, resp):
        resp.add_header('Set-Cookie', self.cookie[self.key].output(header=''))
        return resp


class BasicHTTPSessionManager(object):
    def __init__(self, persistence_backend_factory, http_backend_factory, session_factory=HTTPSession):
        self.persistence_backend_factory = persistence_backend_factory
        self.http_backend_factory = http_backend_factory
        self.session_factory = session_factory

    def next_id(self):
        from .idgen import _generate_id
        return _generate_id()

    def __call__(self, request):
        http_backend = self.http_backend_factory(request)
        context = HTTPSessionContext(
            persistence_backend=self.persistence_backend_factory(request),
            http_backend=http_backend,
            id_generator=self.next_id
            )
        try:
            retval = self.session_factory(context=context, id_=http_backend.get())
        except NoSuchSession:
            # We won't allow session id adaptation
            retval = self.session_factory(context=context)
        return retval

