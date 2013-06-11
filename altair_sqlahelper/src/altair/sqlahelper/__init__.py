# This package may contain traces of nuts
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zope.interface import directlyProvides
from pyramid.settings import asbool
from .interfaces import ISessionMaker

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
        engine = create_engine(url, echo=echo)

        Session = sessionmaker(bind=engine)
        directlyProvides(Session, ISessionMaker)
        config.registry.registerUtility(Session, name=name)

def includeme(config):
    results = from_settings(config.registry.settings)
    register_sessionmakers(config, results)

def get_sessionmaker(request, name=""):
    return request.registry.queryUtility(ISessionMaker, name=name)

def get_db_session(request, name=""):
    sessions = request.environ.get('altair.sqlahelper.sessions', {})
    if name in sessions:
        return sessions[name]

    Session = get_sessionmaker(request, name)
    session = Session()
    sessions[name] = session
    request.environ['altair.sqlahelper.sessions'] = sessions
    return session
