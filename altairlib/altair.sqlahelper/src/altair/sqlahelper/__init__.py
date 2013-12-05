# This package may contain traces of nuts
import logging
import re
import contextlib

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import pool 
from zope.interface import directlyProvides
from pyramid.settings import asbool

from .interfaces import ISessionMaker

logger = logging.getLogger(__name__)

url_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.url")
echo_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.echo")
session_class_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.session_class")
pool_class_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.pool_?class")
pool_recycle_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.pool_recycle")
pool_size_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.pool_size")
pool_timeout_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.pool_timeout")

def asint(value):
    value = value.strip()
    if value == '':
        return None
    return int(value)

def from_settings(settings):
    results = {}

    def param_match(key, value, matcher, param_name, coercer=None):
        matched = matcher.match(key)
        if matched:
            name = matched.groupdict()['name']
            c = results.get(name, {})
            if coercer is not None:
                value = coercer(value)
            c[param_name] = value
            results[name] = c
    for key, value in settings.items():
        param_match(key, value, url_key_pt, 'url')
        param_match(key, value, echo_key_pt, 'echo', asbool)
        param_match(key, value, session_class_key_pt, 'session_class')
        param_match(key, value, pool_class_key_pt,    'pool_class')
        param_match(key, value, pool_recycle_key_pt,  'pool_recycle', asint)
        param_match(key, value, pool_size_key_pt,     'pool_size', asint)
        param_match(key, value, pool_timeout_key_pt,  'pool_timeout', asint)
    return results


pool_class_map = {
    'queue': pool.QueuePool,
    'null': pool.NullPool,
    }

def register_sessionmakers(config, urls):
    for name, c in urls.items():
        if 'url' not in c:
            continue

        url = c['url']
        echo = c.get('echo', False)

        session_class_name = c.get('session_class', None)
        if session_class_name is not None:
            session_class = config.maybe_dotted(session_class_name)
        else:
            session_class = None

        extra_params = {}

        pool_class_name = c.get('pool_class', None)
        if pool_class_name is not None:
            pool_class = pool_class_map.get(pool_class_name, None)
            if pool_class is None:
                pool_class = config.maybe_dotted(pool_class_name)
        else:
            pool_class = None

        if pool_class is not None:
            extra_params['poolclass'] = pool_class

        def assign_extra_param(key):
            value = c.get(key, None)
            if value is not None:
                extra_params[key] = value

        assign_extra_param('pool_recycle')
        assign_extra_param('pool_size')
        assign_extra_param('pool_timeout')

        engine = create_engine(
            url,
            echo=echo,
            **extra_params
            )

        register_sessionmaker_with_engine(config.registry, name, engine, session_class)

def register_sessionmaker_with_engine(registry, name, engine, class_=None):
    kwargs = {}
    if class_ is not None:
        kwargs['class_'] = class_
    Session = sessionmaker(bind=engine, **kwargs)
    directlyProvides(Session, ISessionMaker)
    registry.registerUtility(Session, name=name)

def includeme(config):
    results = from_settings(config.registry.settings)
    register_sessionmakers(config, results)
    config.add_tween('altair.sqlahelper.CloserTween')

def get_sessionmaker(request, name=""):
    Session = request.registry.queryUtility(ISessionMaker, name=name)
    if Session is None:
        message = "session maker named '{0}' is None".format(name)
        logger.warning(message)
        raise Exception(message)
    return Session

def get_db_session(request, name=""):
    sessions = request.environ.get('altair.sqlahelper.sessions', {})
    if name in sessions:
        return sessions[name]

    Session = get_sessionmaker(request, name)
    session = Session()
    sessions[name] = session
    request.environ['altair.sqlahelper.sessions'] = sessions
    return session

class CloserTween(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        try:
            return self.handler(request)
        finally:
            self.close_sessions(request)

    def close_sessions(self, request):
        sessions = request.environ.get('altair.sqlahelper.sessions', {})
        for name in sessions.keys():
            session = sessions.pop(name)
            session.close()


@contextlib.contextmanager
def isolated_transaction(sessionmaker):
    session = sessionmaker()
    try:
        yield session
    finally:
        session.commit()
        session.close()

@contextlib.contextmanager
def named_transaction(request, name):
    session = get_db_session(request, name=name)
    try:
        yield session
    finally:
        session.commit()
