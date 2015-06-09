# -*- coding: utf-8 -*-
"""ファミポート用WebAPI
"""
import pyramid.config
import sqlalchemy as sa
import sqlalchemy.pool as sa_pool
import sqlahelper


def main(global_config, **local_config):
    """ファミポートAPIサーバのエントリーポイント"""
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(
        settings, poolclass=sa_pool.NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = pyramid.config.Configurator(
        settings=settings, root_factory='.resources.famiport_resource_factory')

    config.include(includeme, '/famiport/')
    config.include('altair.app.ticketing.famiport.scripts')

    return config.make_wsgi_app()


def includeme(config):
    # 予済
    config.add_route('famiport.api.reservation.inquiry', '/reservation/inquiry')  # 予約照会
    config.add_route('famiport.api.reservation.payment', '/reservation/payment')  # 入金発券
    config.add_route('famiport.api.reservation.completion', '/reservation/completion')  # 入金発券完了
    config.add_route('famiport.api.reservation.cancel', '/reservation/cancel')  # 入金発券取消
    config.add_route('famiport.api.reservation.information', '/reservation/information')  # 案内通信
    config.add_route('famiport.api.reservation.customer', '/reservation/customer')  # 顧客情報取得

    config.scan('.views')
    config.scan('..builders')

    config.add_renderer('famiport-xml', 'altair.app.ticketing.famiport.renderers.famiport_renderer_factory')
