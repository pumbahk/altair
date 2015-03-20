# -*- coding:utf-8 -*-
import json
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import PredicateMismatch
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper
from altair.app.ticketing.cart.rendering import selectable_renderer

def setup_static_views(config):
    config.add_static_view('static', 'altair.app.ticketing.orderreview:static', cache_max_age=3600)
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
    ## review
    config.add_route('order_review.index', '/', factory='.resources.LandingViewResource')
    config.add_route('order_review.guest', '/guest')  # old url
    config.add_route('order_review.form', '/form', factory='.resources.LandingViewResource')
    config.add_route('order_review.show', '/show', factory='.resources.OrderReviewResource')

    ## qr
    config.add_route('order_review.qr_print', '/qr/print', factory='.resources.QRViewResource')
    config.add_route('order_review.qr_send', '/qr/send', factory='.resources.QRViewResource')
    config.add_route('order_review.qr', '/qr/{ticket_id}/{sign}/ticket', factory='.resources.QRViewResource')
    config.add_route('order_review.qr_confirm', '/qr/{ticket_id}/{sign}/', factory='.resources.QRViewResource')
    config.add_route('order_review.qrdraw', '/qr/{ticket_id}/{sign}/image', factory='.resources.QRViewResource')

    ## orion
    config.add_route('order_review.orion_send', '/qr/eg_send', factory='.resources.EventGateViewResource')
    config.add_route('order_review.orion_draw', '/qr/eg_print/{token}/{serial}/{sign}', factory='.resources.EventGateViewResource')

    ## mypage
    config.add_route('mypage.show', '/mypage', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.mailmag.confirm', '/mypage/mailmag/confirm', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.mailmag.complete', '/mypage/mailmag/complete', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.order.show', '/mypage/order/show', factory='.resources.OrderReviewResource')

    ## misc
    config.add_route('contact', '/contact', factory='.resources.ContactViewResource')

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='.resources.DefaultResource'
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

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.include('altair.app.ticketing.cart')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_mobile')
    config.include('altair.app.ticketing.cart.import_mail_module')
    config.include('altair.app.ticketing.cart.setup_payment_delivery_plugins')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')
    config.include('altair.app.ticketing.cart.setup_auth')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    config.include(setup_static_views)
    config.include('.')
    config.include('.view_context')
    config.scan(".views")
    config.scan(".panels")
    
    return config.make_wsgi_app()


