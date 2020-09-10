# -*- coding:utf-8 -*-
import sqlahelper

from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from pyramid.authorization import ACLAuthorizationPolicy


def setup_auth(config):
    config.include('altair.auth')
    from altair.auth import set_auth_policy
    from altair.app.ticketing.security import AuthModelCallback
    set_auth_policy(config, AuthModelCallback(config))
    config.set_authorization_policy(ACLAuthorizationPolicy())


def includeme(config):
    config.add_route("performances.rakuten_tv_setting.index", "/events/performances/rakuten_tv_setting/index/{performance_id}", factory=".resources.RakutenTvSettingResource")
    config.add_route("ticket_api.availability_check", "/ticket_api/availability_check")
    config.scan('.')


def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings
    )
    config.include('altair.app.ticketing.setup_beaker_cache')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.sqlahelper')
    config.include('altair.pyramid_dynamic_renderer')
    config.include(setup_auth)

    config.add_route("performances.rakuten_tv_setting.index", "/performances/rakuten_tv_setting/index/{performance_id}", factory=".resources.RakutenTvSettingResource")

    # Rakuten TV API
    config.add_route("ticket_api.availability_check", "/ticket_api/availability_check")
    config.include('.')

    return config.make_wsgi_app()