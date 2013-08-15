# This package may contain traces of nuts
import logging
import re
import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zope.interface import directlyProvides
from pyramid.settings import asbool

from altair.logicaldeleting import LogicalDeletableSession
from .interfaces import ISessionMaker

logger = logging.getLogger(__name__)

url_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.url")
echo_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.echo")


def param_match(key, value, matcher, param_name, results):
    matched = matcher.match(key)
    if matched:
        name = matched.groupdict()['name']
        c = results.get(name, {})
        c[param_name] = value
        results[name] = c


def from_settings(settings):
    results = {}
    for key, value in settings.items():
        param_match(key, value, url_key_pt, 'url', results)
        param_match(key, asbool(value), echo_key_pt, 'echo', results)
    return results


def register_sessionmakers(config, urls):
    for name, c in urls.items():
        if 'url' not in c:
            continue
        url = c['url']
        echo = c.get('echo', False)
        engine = create_engine(url, echo=echo,
                               pool_recycle=0)

        Session = sessionmaker(bind=engine, class_=LogicalDeletableSession)
        directlyProvides(Session, ISessionMaker)
        config.registry.registerUtility(Session, name=name)

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
