# -*- coding: utf-8 -*-
"""ファミポート用WebAPI
"""
import pyramid.config
import sqlalchemy as sa
import sqlalchemy.pool as sa_pool
import sqlahelper

from altair.app.ticketing.wsgi import direct_static_serving_filter_factory

STATIC_URL_PREFIX = '/static/'
STATIC_URL_S3_PREFIX = '/lots/static/'
STATIC_ASSET_SPEC = 'altair.app.ticketing.lots:static/'
CART_STATIC_URL_PREFIX = '/c_static/'
CART_STATIC_S3_URL_PREFIX = '/cart/static/'
CART_STATIC_ASSET_SPEC = 'altair.app.ticketing.cart:static/'
FC_AUTH_URL_PREFIX = '/fc_auth/static/'
FC_AUTH_STATIC_ASSET_SPEC = "altair.app.ticketing.fc_auth:static/"


def main(global_config, **local_config):
    """ファミポートAPIサーバのエントリーポイント"""
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(
        settings, poolclass=sa_pool.NullPool, isolation_level='READ COMMITED')
    sqlahelper.add_engine(engine)

    config = pyramid.config.Configurator(
        settings=settings, root_factory='.resources.famiport_resource_factory')

    config.include(includeme, '/famiport/')
    config.include('altair.app.ticketing.famiport.scripts')

    app = config.make_wsgi_app()
    direct_static_server = direct_static_serving_filter_factory({
        STATIC_URL_PREFIX: STATIC_ASSET_SPEC,
        CART_STATIC_URL_PREFIX: CART_STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
        })
    return direct_static_server(global_config, app)


def includeme(config):
    # 予済
    config.add_route('famiport.api.reservation.inquiry', '/reservation/inquiry')  # 予約照会
    config.add_route('famiport.api.reservation.payment', '/reservation/payment')  # 入金発券
    config.add_route('famiport.api.reservation.completion', '/reservation/completion')  # 入金発券完了
    config.add_route('famiport.api.reservation.cancel', '/reservation/cancel')  # 入金発券取消
    config.add_route('famiport.api.reservation.information', '/reservation/information')  # 案内通信
    config.add_route('famiport.api.reservation.customer', '/reservation/customer')  # 顧客情報取得

    config.scan('.views')

    config.add_renderer('famiport-xml', 'altair.app.ticketing.famiport.renderers.famiport_renderer_factory')
