# encoding: utf-8

import sqlahelper

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.exceptions import Forbidden
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from altair.app.ticketing.authentication.config import authentication_policy_factory


def setup_auth(config):
    config.include('altair.auth.config')
    config.set_authentication_policy(authentication_policy_factory(
                config,'altair.ticketing.admin.authentication.policy'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    def forbidden_handler(context, request):
        raise Forbidden()
    config.set_forbidden_handler(forbidden_handler)

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='.resources.ResaleResource'
    )
    config.include('pyramid_dogpile_cache')
    config.include('altair.httpsession.pyramid')
    config.include('altair.sqlahelper')
    config.include('altair.restful_framework')

    config.include(setup_auth)

    config.include('.api', route_prefix='/api')
    config.scan('.')

    return config.make_wsgi_app()