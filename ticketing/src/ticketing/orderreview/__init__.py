# -*- coding:utf-8 -*-
import json
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import PredicateMismatch
# from ticketing.cart.interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
# from ticketing.cart.interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

from sqlalchemy import engine_from_config
import sqlahelper

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings)
    sqlahelper.add_engine(engine)

    my_session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.set_root_factory('.resources.OrderReviewResource')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'ticketing.orderreview:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)

    ### include altair.*
    config.include('altair.exclog')
    config.include('altair.browserid')

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={"ticketing.cart:static/": "/cart/static/"}))

    config.add_tween('ticketing.cart.tweens.OrganizationPathTween')

    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.cart')
    config.include('ticketing.cart.import_mail_module')
    config.include("ticketing.qr")
    config.scan('ticketing.cart.views')

    config.commit() #override qr plugins view(e.g. qr)
    config.include(".plugin_override")
    config.include('altair.mobile')

    config.include(import_selectable_renderer)
    config.include(import_view)
    config.include(import_exc_view)
    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    
    config.scan(".views")
    
    return config.make_wsgi_app()

def import_selectable_renderer(config):
    ### selectable renderer
    from pyramid.interfaces import IDict
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

def import_view(config):
    ## reivew
    config.add_route('order_review.form', '/')
    config.add_route('order_review.show', '/show')
    
    ## qr
    config.add_route('order_review.qr_print', '/qr/print')
    config.add_route('order_review.qr_send', '/qr/send')
    config.add_route('order_review.qr', '/qr/{ticket_id}/{sign}/ticket')
    config.add_route('order_review.qr_confirm', '/qr/{ticket_id}/{sign}/')
    config.add_route('order_review.qrdraw', '/qr/{ticket_id}/{sign}/image')

    ## misc
    config.add_route('contact', '/contact')

def import_exc_view(config):
    ## exc
    from ticketing.cart.selectable_renderer import selectable_renderer
    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer=selectable_renderer("%(membership)s/errors/not_found.html"))
    config.add_view('.views.notfound_view', context=HTTPNotFound,  renderer=selectable_renderer("%(membership)s/errors_mobile/not_found.html"), request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.views.exception_view',  context=StandardError, renderer=selectable_renderer("%(membership)s/errors/error.html"))
    config.add_view('.views.exception_view', context=StandardError,  renderer=selectable_renderer("%(membership)s/errors_mobile/error.html"), request_type='altair.mobile.interfaces.IMobileRequest')



