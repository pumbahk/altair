from pyramid.config import Configurator
from pyramid_beaker import (
    session_factory_from_settings,
    set_cache_regions_from_settings,
    )
from pyramid.httpexceptions import HTTPNotFound
import json
from ticketing.payments.interfaces import IOrderPayment, IOrderDelivery
from pyramid.interfaces import IDict
from sqlalchemy import engine_from_config
import sqlahelper

def add_routes(config):
    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')
    config.add_route('cart.payment', 'payment/sales/{sales_segment_id}')
    config.add_route('payment.confirm', 'confirm')
    config.add_route('payment.finish', 'completed')

    config.add_route('order_review.form', '/review')
    config.add_route('order_review.show', '/review/show')

def add_cart_views(config):
    from ticketing.cart.selectable_renderer import selectable_renderer
    config.add_view('.views.PaymentView', route_name='cart.payment', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/payment.html"))
    config.add_view('.views.PaymentView', route_name='cart.payment', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/payment.html"))
    config.add_view('.views.ConfirmView', attr='get', route_name='payment.confirm', request_method="GET", renderer=selectable_renderer("carts/%(membership)s/confirm.html"))
    config.add_view('.views.ConfirmView', attr='get', route_name='payment.confirm', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", renderer=selectable_renderer("carts_mobile/%(membership)s/confirm.html"))

def add_viewlets(config):
    from ticketing.payments.plugins import MULTICHECKOUT_PAYMENT_PLUGIN_ID, SEJ_PAYMENT_PLUGIN_ID
    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % SEJ_PAYMENT_PLUGIN_ID,
                    renderer='carts/sej_payment_complete.html')
    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % SEJ_PAYMENT_PLUGIN_ID, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/sej_payment_complete.html")

    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                    renderer='carts/multicheckout_payment_complete.html')
    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % MULTICHECKOUT_PAYMENT_PLUGIN_ID, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/multicheckout_payment_complete.html")

def includeme(config):
    pass

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool,
                                isolation_level='READ COMMITTED',
                                pool_recycle=60)
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory='.resources.Bj89erCartResource',
                          session_factory=session_factory)
    config.registry['sa.engine'] = engine

    from ticketing import setup_standard_renderers
    config.include(setup_standard_renderers)

    config.add_static_view('static', 'ticketing.bj89ers:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)

    ## includes altair.*
    config.include('altair.mobile')

    ## includes ticketing.*
    config.include('ticketing.cart')
    config.include("ticketing.cart.selectable_renderer")
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')

    ## include .
    config.scan('.')

    ## routes and views
    config.include(add_routes)
    config.include(add_cart_views)

    ## tweens
    config.add_tween('ticketing.cart.tweens.altair_host_tween_factory',
        under='altair.mobile.tweens.mobile_encoding_convert_factory')

    config.set_cart_getter('ticketing.cart.api.get_cart_safe')

    ## events
    config.add_subscriber('.subscribers.add_helpers',     'pyramid.events.BeforeRender')
    config.add_subscriber('.api.on_order_completed',      'ticketing.cart.events.OrderCompleted')
    config.add_subscriber('.sendmail.on_order_completed', 'ticketing.cart.events.OrderCompleted')

    ## overrides
    config.commit()
    config.include(add_viewlets)

    return config.make_wsgi_app()
