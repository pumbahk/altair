from ticketing.payments.exceptions import PaymentPluginException
from pyramid.httpexceptions import HTTPNotFound
from ticketing.payments.interfaces import IOrderPayment
from ticketing.cart.selectable_renderer import selectable_renderer

def setup_cart(config):
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    config.add_subscriber('.subscribers.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    config.set_cart_getter('ticketing.cart.api.get_cart_safe')
    config.commit()

def setup_excviews(config):
    config.add_view('.excviews.OutTermSalesView', attr='pc', context='ticketing.cart.exceptions.OutTermSalesException', renderer='carts/out_term_sales.html')
    config.add_view('.excviews.OutTermSalesView', attr='mobile', context='ticketing.cart.exceptions.OutTermSalesException', renderer='carts_mobile/out_term_sales.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.notfound_view', context=HTTPNotFound, renderer='errors/not_found.html', )
    config.add_view('.excviews.notfound_view', context=HTTPNotFound,  renderer='errors_mobile/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.forbidden_view', context='pyramid.httpexceptions.HTTPForbidden', renderer='errors/not_found.html', )
    config.add_view('.excviews.forbidden_view', context='pyramid.httpexceptions.HTTPForbidden', renderer='errors_mobile/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors/error.html')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors_mobile/error.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.exception_view',  context=StandardError, renderer='errors/error.html')
    config.add_view('.excviews.exception_view', context=StandardError,  renderer='errors_mobile/error.html', request_type='altair.mobile.interfaces.IMobileRequest')
    ## xxxx
    config.add_view('.excviews.exception_view', context=Exception, renderer='errors/not_found.html', )
    config.add_view('.excviews.exception_view', context=Exception, renderer='errors_mobile/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')

def setup_views(config):
    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')

    config.add_route('order_review.form', '/review')
    config.add_route('order_review.show', '/review/show')

    config.add_view('.views.IndexView', attr='notready', route_name='notready', renderer='carts/notready.html')
    config.add_view('.views.IndexView', attr='notready', request_type='altair.mobile.interfaces.IMobileRequest', route_name='notready', renderer='carts_mobile/notready.html')
    config.add_view('.views.IndexView', route_name='index', attr='get', request_method='GET', renderer='carts/form.html', 
                    decorator='ticketing.fanstatic.with_jquery')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr='get', request_method='GET', renderer='carts_mobile/form.html')

    config.add_view('.views.IndexView', route_name='index', attr='post', request_method='POST', renderer='carts/form.html', 
                    decorator='ticketing.fanstatic.with_jquery')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr='post', request_method='POST', renderer='carts_mobile/form.html')

    config.add_view('.views.PaymentView', route_name='cart.payment', attr='post', request_method='POST', renderer=selectable_renderer('carts/%(membership)s/payment.html'))
    config.add_view('.views.PaymentView', request_type='altair.mobile.interfaces.IMobileRequest',  route_name='cart.payment', 
                    attr='post', request_method='POST', renderer=selectable_renderer('carts_mobile/%(membership)s/payment.html'))

    config.add_view('.views.CompleteView', route_name='payment.finish', request_method='POST', renderer='carts/completion.html')
    config.add_view('.views.CompleteView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='payment.finish', 
                    request_method='POST', renderer='carts_mobile/completion.html')

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr='get', request_method='GET', renderer='order_review/form.html')
    config.add_view('.views.OrderReviewView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='order_review.form',
                    attr='get', request_method='GET', renderer='order_review_mobile/form.html')

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr='post', request_method='POST', renderer='order_review/show.html')
    config.add_view('.views.OrderReviewView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='order_review.show',
                    attr='post', request_method='POST', renderer='order_review_mobile/show.html')

    config.add_view('.views.order_review_form_view', name='order_review_form', renderer='order_review/form.html')
    config.add_view('.views.order_review_form_view', name='order_review_form', renderer='order_review_mobile/form.html', request_type='altair.mobile.interfaces.IMobileRequest')

    config.add_view('.views.contact_view', route_name='contact', renderer='static/contact.html')
    config.add_view('.views.contact_view', route_name='contact', renderer='static_mobile/contact.html', request_type='altair.mobile.interfaces.IMobileRequest')

def setup_plugins_views(config):
    PAYMENT_PLUGIN_ID_SEJ = 3
    PAYMENT_PLUGIN_ID_CARD = 1

    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_SEJ,
                    renderer='carts/sej_payment_complete.html')
    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_SEJ, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer='carts_mobile/sej_payment_complete.html')

    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_CARD,
                    renderer='carts/multicheckout_payment_complete.html')
    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_CARD, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer='carts_mobile/multicheckout_payment_complete.html')

def setup_order_product_attribute_metadata(config):
    from ticketing.orders.api import get_metadata_provider_registry
    from .metadata import metadata_provider
    get_metadata_provider_registry(config.registry).registerProvider(metadata_provider)
    
def includeme(config):
    config.include(setup_cart)
    config.include('altair.mobile')
    config.include(setup_views)
    config.include(setup_excviews)
    config.include(setup_plugins_views)

    config.include('ticketing.orders')
    config.include(setup_order_product_attribute_metadata)

    config.include('.89ers')
    config.include('.bambitious')
