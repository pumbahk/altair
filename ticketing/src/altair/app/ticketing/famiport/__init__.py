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

    config.include(setup_routes)
    app = config.make_wsgi_app()
    direct_static_server = direct_static_serving_filter_factory({
        STATIC_URL_PREFIX: STATIC_ASSET_SPEC,
        CART_STATIC_URL_PREFIX: CART_STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
        })
    direct_static_server(global_config, app)


def setup_routes(config):
    config.add_route('famiport.ping.', 'api/ping/')  # 疎通確認用
    # 予済
    config.add_route('famiport.api.search', 'api/search/')  # 予約照会
    config.add_route('famiport.api.lock', 'api/lock/')  # 入金発券通信
    config.add_route('famiport.api.finsh', 'api/finish/')  # 入金発券完了通信
    config.add_route('famiport.api.unlock', 'api/unlock/')  # 入金発券取消通信
    config.add_route('famiport.api.information', 'api/information/')  # 案内通信
    config.add_route('famiport.api.customer', 'api/customer/')  # 顧客情報取得通信
