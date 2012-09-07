from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.httpexceptions import HTTPNotFound

from ticketing.cart.interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
from ticketing.cart.interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

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
    config.add_static_view('static', 'ticketing.bj89ers:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.cart.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    config.commit()

    config.include('..mobile')

    config.add_route('contact', '/contact')
    config.add_route('order_review.form', '/')
    config.add_route('order_review.show', '/show')

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr="get", request_method="GET", renderer="order_review/form.html")
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.form',
                    attr="get", request_method="GET", renderer="order_review_mobile/form.html")

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr="post", request_method="POST", renderer="order_review/show.html")
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.show',
                    attr="post", request_method="POST", renderer="order_review_mobile/show.html")

    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review/form.html")
    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review_mobile/form.html", request_type='ticketing.cart.interfaces.IMobileRequest')

    config.add_view('.views.contact_view', route_name="contact", renderer="static/contact.html")
    config.add_view('.views.contact_view', route_name="contact", renderer="static_mobile/contact.html", request_type='ticketing.cart.interfaces.IMobileRequest')
    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer="errors/not_found.html", )
    config.add_view('.views.notfound_view', context=HTTPNotFound,  renderer="errors_mobile/not_found.html", request_type='ticketing.cart.interfaces.IMobileRequest')
    config.add_view('.views.exception_view',  context=StandardError, renderer="errors/error.html")
    config.add_view('.views.exception_view', context=StandardError,  renderer="errors_mobile/error.html", request_type='ticketing.cart.interfaces.IMobileRequest')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    return config.make_wsgi_app()
