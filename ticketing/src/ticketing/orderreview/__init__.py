# -*- coding:utf-8 -*-
import json
from pyramid.config import Configurator
from pyramid_beaker import (
    session_factory_from_settings,
    set_cache_regions_from_settings,
    )
from pyramid.httpexceptions import HTTPNotFound
from pyramid.exceptions import PredicateMismatch
# from ticketing.cart.interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
# from ticketing.cart.interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

from sqlalchemy import engine_from_config
import sqlahelper

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool,
                                pool_recycle=60) 
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory='.resources.OrderReviewResource',
                          session_factory=session_factory)
    from ticketing import setup_standard_renderers
    config.include(setup_standard_renderers)

    config.add_static_view('static', 'ticketing.orderreview:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)

    ### includes altair.*
    config.include('altair.exclog')
    config.include('altair.exclog')
    config.include('altair.browserid')
    config.include("altair.cdnpath")
    config.include('altair.mobile')

    ## includes ticketing.*
    config.include('ticketing.mails')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.cart')
    config.include("ticketing.qr")
    config.include("ticketing.cart.selectable_renderer")

    ## routes and views
    config.include(import_view)
    config.include(import_exc_view)
    config.scan(".views")
   
    ## tweens
    config.add_tween('ticketing.cart.tweens.altair_host_tween_factory',
        under='altair.mobile.tweens.mobile_encoding_convert_factory')

    ## events
    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    ## overrides
    config.commit()
    config.include(".plugin_override")

    return config.make_wsgi_app()

def import_view(config):
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
