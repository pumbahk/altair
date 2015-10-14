# -*- coding:utf-8 -*-
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

def setup_static_views(config):
    config.add_static_view('static', 'altair.app.ticketing.coupon:static', cache_max_age=3600)
    config.add_static_view('static_', 'altair.app.ticketing.cart:static', cache_max_age=3600)
    config.add_static_view('img', 'altair.app.ticketing.cart:static', cache_max_age=3600)

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    settings = config.registry.settings
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"],
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
            mapping={"altair.app.ticketing.cart:static/": "/cart/static/"}))

def includeme(config):
    ## coupon
    config.add_route('coupon', '/{reserved_number}', factory='.resources.CouponViewResource')
    config.add_route('coupon.admission', '/{reserved_number}/use/{token_id}', factory='.resources.CouponViewResource')
    config.add_route('coupon.notfound', '/notfound/', factory='.resources.CouponViewResource')

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        )
    config.include('altair.app.ticketing.setup_beaker_cache')

    config.include('pyramid_layout')

    ### include altair.*
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.mq')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.sqlahelper')

    config.include('altair.app.ticketing.cart')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_payment_delivery_plugins')
    config.include('altair.app.ticketing.cart.setup_mobile')
    config.include('altair.app.ticketing.cart.setup_cart_interface')
    config.include('altair.app.ticketing.cart.import_mail_module')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')

    config.add_subscriber('..orderreview.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    config.include(setup_static_views)
    config.include('.view_context')
    config.include('.')
    config.scan(".views")

    return config.make_wsgi_app()
