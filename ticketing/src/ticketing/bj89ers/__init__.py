from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid.httpexceptions import HTTPNotFound
import json
from ..payments.exceptions import PaymentPluginException
from ticketing.payments.interfaces import IPaymentPlugin, IOrderPayment
from ticketing.payments.interfaces import IDeliveryPlugin, IOrderDelivery
from ticketing.cart.interfaces import ICartDelivery
from ticketing.cart.interfaces import ICartDelivery
from pyramid.interfaces import IDict
from sqlalchemy import engine_from_config
import sqlahelper

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    my_session_factory = session_factory_from_settings(settings)
    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.set_root_factory('.resources.Bj89erCartResource')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
    config.add_static_view('static', 'ticketing.bj89ers:static', cache_max_age=3600)
    config.add_static_view('static_', 'ticketing.cart:static', cache_max_age=3600)

    ### selectable renderer
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)
    selector = config.maybe_dotted("ticketing.cart.selectable_renderer.ByDomainMappingSelector")(domain_candidates)
    config.add_selectable_renderer_selector(selector)


    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    config.add_subscriber('.api.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    config.commit()

    config.include('..mobile')

    config.add_route('order_review.form', '/review')
    config.add_route('order_review.show', '/review/show')

    config.add_view('.views.IndexView', attr='notready', route_name='notready', renderer='carts/notready.html')
    config.add_view('.views.IndexView', attr='notready', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='notready', renderer='carts_mobile/notready.html')
    config.add_view('.views.IndexView', route_name='index', attr="get", request_method='GET', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr="get", request_method='GET', renderer='carts_mobile/form.html')

    config.add_view('.views.IndexView', route_name='index', attr="post", request_method='POST', renderer='carts/form.html')
    config.add_view('.views.IndexView', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr="post", request_method='POST', renderer='carts_mobile/form.html')

    config.add_view('.views.PaymentView', route_name='cart.payment', attr="post", request_method="POST", renderer="carts/payment.html")
    config.add_view('.views.PaymentView', request_type='ticketing.mobile.interfaces.IMobileRequest',  route_name='cart.payment', 
                    attr="post", request_method="POST", renderer="carts_mobile/payment.html")

    config.add_view('.views.CompleteView', route_name='payment.finish', request_method="POST", renderer="carts/completion.html")
    config.add_view('.views.CompleteView', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='payment.finish', 
                    request_method="POST", renderer="carts_mobile/completion.html")

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr="get", request_method="GET", renderer="order_review/form.html")
    config.add_view('.views.OrderReviewView', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='order_review.form',
                    attr="get", request_method="GET", renderer="order_review_mobile/form.html")

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr="post", request_method="POST", renderer="order_review/show.html")
    config.add_view('.views.OrderReviewView', request_type='ticketing.mobile.interfaces.IMobileRequest', route_name='order_review.show',
                    attr="post", request_method="POST", renderer="order_review_mobile/show.html")

    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review/form.html")
    config.add_view('.views.order_review_form_view', name="order_review_form", renderer="order_review_mobile/form.html", request_type='ticketing.mobile.interfaces.IMobileRequest')

    config.add_view('.views.contact_view', route_name="contact", renderer="static/contact.html")
    config.add_view('.views.contact_view', route_name="contact", renderer="static_mobile/contact.html", request_type='ticketing.mobile.interfaces.IMobileRequest')
    config.add_view('.views.notfound_view', context=HTTPNotFound, renderer="errors/not_found.html", )
    config.add_view('.views.notfound_view', context=HTTPNotFound,  renderer="errors_mobile/not_found.html", request_type='ticketing.mobile.interfaces.IMobileRequest')
    config.add_view('.views.forbidden_view', context="pyramid.httpexceptions.HTTPForbidden", renderer="errors/not_found.html", )
    config.add_view('.views.forbidden_view', context="pyramid.httpexceptions.HTTPForbidden", renderer="errors_mobile/not_found.html", request_type='ticketing.mobile.interfaces.IMobileRequest')
    config.add_view('.views.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors/error.html')
    config.add_view('.views.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors_mobile/error.html', request_type='ticketing.mobile.interfaces.IMobileRequest')
    config.add_view('.views.exception_view',  context=StandardError, renderer="errors/error.html")
    config.add_view('.views.exception_view', context=StandardError,  renderer="errors_mobile/error.html", request_type='ticketing.mobile.interfaces.IMobileRequest')
    ## xxxx
    config.add_view('.views.exception_view', context=Exception, renderer="errors/not_found.html", )
    config.add_view('.views.exception_view', context=Exception, renderer="errors_mobile/not_found.html", request_type='ticketing.mobile.interfaces.IMobileRequest')
    # @view_config()

    PAYMENT_PLUGIN_ID_SEJ = 3
    PAYMENT_PLUGIN_ID_CARD = 1

    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ,
                    renderer='carts/sej_payment_complete.html')
    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ, request_type='ticketing.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/sej_payment_complete.html")

    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD,
                    renderer='carts/multicheckout_payment_complete.html')
    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD, request_type='ticketing.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/multicheckout_payment_complete.html")

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.add_subscriber('.sendmail.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    return config.make_wsgi_app()
