# -*- coding: utf-8 -*-
"""Famiポート用WebAPI (Altair側)
"""
import pyramid.config
import sqlalchemy as sa
import sqlalchemy.pool as sa_pool
import sqlahelper
import transaction

def main(global_config, **local_config):
    """FamiポートAPIサーバのエントリーポイント"""
    settings = dict(global_config)
    settings.update(local_config)

    from altair.app.ticketing import install_ld, setup_mailtraverser, register_globals, setup_beaker_cache
    install_ld()
    from sqlalchemy.pool import NullPool
    engine = sa.engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    with transaction.manager:
        config = pyramid.config.Configurator(
            settings=settings, root_factory='.resources.userside_famiport_resource_factory')

        config.include(setup_beaker_cache)
        config.include("pyramid_mako")
        config.add_mako_renderer('.html')
        config.add_mako_renderer('.txt')
        config.include('altair.app.ticketing.renderers')
        config.include("pyramid_fanstatic")
        config.include('pyramid_tm')
        config.include('pyramid_mailer')
        config.include('altair.queryprofile')
        config.include(setup_mailtraverser)
        config.include('altair.exclog')
        config.include('altair.sqlahelper')
        config.include('altair.app.ticketing.famiport.communication')
        config.include('altair.mq')
        config.include('altair.app.ticketing.core')
        config.include('altair.app.ticketing.mails')
        config.include('altair.app.ticketing.authentication')
        config.include('altair.app.ticketing.multicheckout')
        config.include('altair.app.ticketing.checkout')
        config.include('altair.app.ticketing.sej')
        config.include('altair.app.ticketing.sej.userside_impl')
        config.include('altair.app.ticketing.famiport')
        config.include('.')
        return config.make_wsgi_app()

def includeme(config):
    config.add_route('famiport.userside_api.ping', '/ping') # ping
    config.add_route('famiport.userside_api.completed', '/completed')  # 完了
    config.add_route('famiport.userside_api.canceled', '/canceled')  # キャンセル (VOIDではない)
    config.add_route('famiport.userside_api.refunded', '/refunded')  # 払戻

    config.scan('.views')
