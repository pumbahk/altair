# coding:utf-8
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import sqlahelper

from sqlalchemy import engine_from_config

from altaircms.security import groupfinder
from altaircms.models import initialize_sql


from pyramid.security import Allow, Authenticated
from pyramid.security import Everyone

class RootFactory(object):
    __name__ = None
    __parent__ = None
    __acl__ = [
        (Allow, Authenticated, 'view'),
        (Allow, 'group:editors', 'edit')
    ]

    def __init__(self, request):
        pass


def api_include(config):
    config.add_route('api_event', '/event/{id}')
    config.add_route('api_event_list', '/event/')


def cms_include(config):
    config.add_route('event', 'event/{id}')
    config.add_route('event_list', 'event')
    config.add_route('page_add', 'event/{event_id}/page/edit')


def front_include(config):
    config.add_route('front', '{page_name}')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)

    # sqlahelper.add_engine(engine)

    authn_policy = AuthTktAuthenticationPolicy(secret='sosecret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    config = Configurator(
        root_factory=RootFactory,
        settings=settings,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy
    )
    config.include('pyramid_tm')

    config.include(api_include, route_prefix='/api')
    config.include(front_include, route_prefix='/f')
    config.include(cms_include, route_prefix='/')

    config.scan("altaircms.views")
    config.add_static_view('static', 'altaircms:static', cache_max_age=3600)

    return config.make_wsgi_app()
