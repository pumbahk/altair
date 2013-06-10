# This package may contain traces of nuts
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zope.interface import Interface, directlyProvides
from pyramid.settings import asbool

url_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.url")
echo_key_pt = re.compile(r"altair\.sqlahelper\.sessions\.(?P<name>\w+)\.echo")


def from_settings(settings):
    results = {}
    for key, value in settings.items():
        url_match = url_key_pt.match(key)
        if url_match:
            name = url_match.groupdict()['name']
            c = results.get(name, {})
            c['url'] = value
            results[name] = c
        echo_match = echo_key_pt.match(key)
        if echo_match:
            name = echo_match.groupdict()['name']
            c = results.get(name, {})
            c['echo'] = asbool(value)
            results[name] = c
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

class ISessionMaker(Interface):
    def __call__():
        """ create new session """
