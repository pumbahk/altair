# -*- coding:utf-8 -*-
import json
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.httpexceptions import HTTPNotFound
from ticketing.cart.selectable_renderer import selectable_renderer

# from ticketing.cart.interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
# from ticketing.cart.interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

from sqlalchemy import engine_from_config
import sqlahelper

def main(global_conf, **settings):
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

    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.cart.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    # config.commit() #これ必要？
    config.include('..mobile')

    config.include(import_selectable_renderer)
    config.include(import_order_review_view)
    config.include(import_misc_view)
    config.include(import_exc_view)
    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    
    config.scan()
    
    return config.make_wsgi_app()

def import_selectable_renderer(config):
    ### selectable renderer
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    selector = config.maybe_dotted("ticketing.cart.selectable_renderer.ByDomainMappingSelector")(domain_candidates)
    config.add_selectable_renderer_selector(selector)


def import_order_review_view(config):
    config.add_route('order_review.form', '/')
    config.add_route('order_review.show', '/show')
    config.add_route('order_review.qr', '/qr/{ticket_id}/{sign}/')
    config.add_route('order_review.qrdraw', '/qr/{ticket_id}/{sign}/image')

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr="get", request_method="GET", renderer=selectable_renderer("%(membership)s/order_review/form.html"))
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.form',
                    attr="get", request_method="GET", renderer=selectable_renderer("%(membership)s/order_review_mobile/form.html"))

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr="post", request_method="POST", renderer=selectable_renderer("%(membership)s/order_review/show.html"))
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.show',
                    attr="post", request_method="POST", renderer=selectable_renderer("%(membership)s/order_review_mobile/show.html"))

    config.add_view('.views.order_review_form_view', context=".views.InvalidForm", renderer=selectable_renderer("%(membership)s/order_review/form.html"))
    config.add_view('.views.order_review_form_view', context=".views.InvalidForm", renderer=selectable_renderer("order_review_mobile%(membership)s/form.html"), request_type='ticketing.cart.interfaces.IMobileRequest')
    
    config.add_view('.views.order_review_qr_html', route_name='order_review.qr', renderer=selectable_renderer("order_review/%(membership)s/qr.html"))

def import_misc_view(config):
    config.add_route('contact', '/contact')
    config.add_view('.views.contact_view', route_name="contact", renderer=selectable_renderer("%(membership)s/static/contact.html"))
    config.add_view('.views.contact_view', route_name="contact", renderer=selectable_renderer("%(membership)s/static_mobile/contact.html"), request_type='ticketing.cart.interfaces.IMobileRequest')


def import_exc_view(config):
    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer=selectable_renderer("%(membership)s/errors/not_found.html"))
    config.add_view('.views.notfound_view', context=HTTPNotFound,  renderer=selectable_renderer("%(membership)s/errors_mobile/not_found.html"), request_type='ticketing.cart.interfaces.IMobileRequest')
    config.add_view('.views.exception_view',  context=StandardError, renderer=selectable_renderer("%(membership)s/errors/error.html"))
    config.add_view('.views.exception_view', context=StandardError,  renderer=selectable_renderer("%(membership)s/errors_mobile/error.html"), request_type='ticketing.cart.interfaces.IMobileRequest')

