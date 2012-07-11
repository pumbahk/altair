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
    config.set_root_factory('.resources.Bj89erCartResource')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'ticketing.bj89ers:static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.scan('ticketing.orders.models')
    config.include('ticketing.cart.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    config.add_subscriber('.api.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    config.commit()

    config.add_tween(".tweens.mobile_encoding_convert_factory")
    #config.add_tween(".tweens.mobile_request_factory")

    config.add_route('order_review.form', '/review')
    config.add_route('order_review.show', '/review/show')

    config.add_view('.views.IndexView', attr='notready', route_name='notready', renderer='carts/notready.html')
    config.add_view('.views.IndexView', attr='notready', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='notready', renderer='carts_mobile/notready.html')
    config.add_view('.views.IndexView', route_name='index', attr="get", request_method='GET', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='index', 
                    attr="get", request_method='GET', renderer='carts_mobile/form.html')

    config.add_view('.views.IndexView', route_name='index', attr="post", request_method='POST', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='index', 
                    attr="post", request_method='POST', renderer='carts_mobile/form.html')

    config.add_view('.views.PaymentView', route_name='cart.payment', attr="post", request_method="POST", renderer="carts/payment.html")
    config.add_view('.views.PaymentView', request_type='ticketing.cart.interfaces.IMobileRequest',  route_name='cart.payment', 
                    attr="post", request_method="POST", renderer="carts_mobile/payment.html")

    config.add_view('.views.CompleteView', route_name='payment.finish', request_method="POST", renderer="carts/completion.html")
    config.add_view('.views.CompleteView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='payment.finish', 
                    request_method="POST", renderer="carts_mobile/completion.html")

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr="get", request_method="GET", renderer="order_review/form.html")
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.form',
                    attr="get", request_method="GET", renderer="order_review_mobile/form.html")

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr="post", request_method="POST")
    config.add_view('.views.OrderReviewView', request_type='ticketing.cart.interfaces.IMobileRequest', route_name='order_review.show',
                    attr="post", request_method="POST", renderer="order_review_mobile/show.html")

    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review/form.html")
    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review_mobile/form.html", request_type='ticketing.cart.interfaces.IMobileRequest')

    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer="errors/not_fount.html")
    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer="errors_mobile/not_fount.html", request_type='ticketing.cart.interfaces.IMobileRequest')
    config.add_view('.views.exception_view', context=Exception, renderer="errors/error.html")
    config.add_view('.views.exception_view', context=Exception, renderer="errors_mobile/error.html", request_type='ticketing.cart.interfaces.IMobileRequest')
    config.add_view('.views.contact_view', route_name="contact", renderer="static/contact.html")
    config.add_view('.views.contact_view', route_name="contact", renderer="static_mobile/contact.html", request_type='ticketing.cart.interfaces.IMobileRequest')

    # @view_config()

    PAYMENT_PLUGIN_ID_SEJ = 3
    PAYMENT_PLUGIN_ID_CARD = 1

    config.add_view('ticketing.cart.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ,
                    renderer='carts/sej_payment_complete.html')
    config.add_view('ticketing.cart.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ, request_type='ticketing.cart.interfaces.IMobileRequest',
                    renderer="carts_mobile/sej_payment_complete.html")

    config.add_view('ticketing.cart.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD,
                    renderer='carts/multicheckout_payment_complete.html')
    config.add_view('ticketing.cart.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD, request_type='ticketing.cart.interfaces.IMobileRequest',
                    renderer="carts_mobile/multicheckout_payment_complete.html")



    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.add_subscriber('.sendmail.on_order_completed', 'ticketing.cart.events.OrderCompleted')

    return config.make_wsgi_app()
