# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    pass

def main(global_conf, **settings):
    from ticketing.logicaldeleting import install as install_ld
    install_ld()

    from sqlalchemy import engine_from_config
    from sqlalchemy.pool import NullPool
    import sqlahelper
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config = Configurator(
        settings=settings,
        session_factory=my_session_factory)
    config.include('.')
    config.include('.demo')
    config.include('pyramid_fanstatic')

    return config.make_wsgi_app()
