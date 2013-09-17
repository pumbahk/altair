from altair.app.ticketing.payments.exceptions import PaymentPluginException
from pyramid.httpexceptions import HTTPNotFound
from altair.app.ticketing.payments.interfaces import IOrderPayment
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer

def setup_cart(config):
    config.include('altair.app.ticketing.checkout')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include('altair.app.ticketing.cart.setup_components')

    config.add_subscriber('.subscribers.on_order_completed', 'altair.app.ticketing.cart.events.OrderCompleted')
    config.set_cart_getter('altair.app.ticketing.cart.api.get_cart_safe')
    config.commit()

def setup_excviews(config):
    config.add_view('.excviews.OutTermSalesView', attr='pc', context='altair.app.ticketing.cart.exceptions.OutTermSalesException', renderer='base/pc/cart/out_term_sales.html')
    config.add_view('.excviews.OutTermSalesView', attr='mobile', context='altair.app.ticketing.cart.exceptions.OutTermSalesException', renderer='base/mobile/cart/out_term_sales.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.notfound_view', context=HTTPNotFound, renderer='base/pc/errors/not_found.html', )
    config.add_view('.excviews.notfound_view', context=HTTPNotFound,  renderer='base/mobile/errors/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.forbidden_view', context='pyramid.httpexceptions.HTTPForbidden', renderer='base/pc/errors/not_found.html', )
    config.add_view('.excviews.forbidden_view', context='pyramid.httpexceptions.HTTPForbidden', renderer='base/mobile/errors/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='altair.app.ticketing.cart:templates/errors/error.html')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='altair.app.ticketing.cart:templates/errors_mobile/error.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.exception_view',  context=StandardError, renderer='base/pc/errors/error.html')
    config.add_view('.excviews.exception_view', context=StandardError,  renderer='base/mobile/errors/error.html', request_type='altair.mobile.interfaces.IMobileRequest')
    ## xxxx
    config.add_view('.excviews.exception_view', context=Exception, renderer='base/pc/errors/not_found.html', )
    config.add_view('.excviews.exception_view', context=Exception, renderer='base/mobile/errors/not_found.html', request_type='altair.mobile.interfaces.IMobileRequest')

def setup_views(config):
    config.add_route('index', '/')
    config.add_route('contact', '/contact')
    config.add_route('notready', '/notready')

    config.add_route('order_review.form', '/review')
    config.add_route('order_review.show', '/review/show')

    config.add_route('cart.payment', '/payment/sales/{sales_segment_id}')
    config.add_route('payment.confirm', '/confirm')
    config.add_route('payment.finish', '/completed')

    config.add_view('.views.IndexView', attr='notready', route_name='notready', renderer='base/pc/cart/notready.html')
    config.add_view('.views.IndexView', attr='notready', request_type='altair.mobile.interfaces.IMobileRequest', route_name='notready', renderer='base/mobile/cart/notready.html')
    config.add_view('.views.IndexView', route_name='index', attr='get', request_method='GET', renderer='base/pc/cart/form.html', 
                    decorator='altair.app.ticketing.fanstatic.with_jquery')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr='get', request_method='GET', renderer='base/mobile/cart/form.html')

    config.add_view('.views.IndexView', route_name='index', attr='post', request_method='POST', renderer='base/pc/cart/form.html', 
                    decorator='altair.app.ticketing.fanstatic.with_jquery')
    config.add_view('.views.IndexView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='index', 
                    attr='post', request_method='POST', renderer='base/mobile/cart/form.html')

    config.add_view('.views.PaymentView', route_name='cart.payment', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/payment.html"))
    config.add_view('.views.PaymentView', route_name='cart.payment', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/payment.html"))
    config.add_view('.views.PaymentView', route_name='cart.payment', attr='post', request_method='POST', renderer=selectable_renderer('%(membership)s/pc/payment.html'))
    config.add_view('.views.PaymentView', request_type='altair.mobile.interfaces.IMobileRequest',  route_name='cart.payment', 
                    attr='post', request_method='POST', renderer=selectable_renderer('%(membership)s/mobile/payment.html'))

    config.add_view('.views.ConfirmView', route_name='payment.confirm', request_method="GET", renderer=selectable_renderer("%(membership)s/pc/confirm.html"))
    config.add_view('.views.ConfirmView', route_name='payment.confirm', request_method="GET", request_type='altair.mobile.interfaces.IMobileRequest', renderer=selectable_renderer("%(membership)s/mobile/confirm.html"))

    config.add_view('.views.CompleteView', route_name='payment.finish', request_method='POST', renderer='base/pc/cart/completion.html')
    config.add_view('.views.CompleteView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='payment.finish', 
                    request_method='POST', renderer='base/mobile/cart/completion.html')

    config.add_view('.views.OrderReviewView', route_name='order_review.form', attr='get', request_method='GET', renderer='base/pc/order_review/form.html')
    config.add_view('.views.OrderReviewView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='order_review.form',
                    attr='get', request_method='GET', renderer='base/mobile/order_review/form.html')

    config.add_view('.views.OrderReviewView', route_name='order_review.show', attr='post', request_method='POST', renderer='base/pc/order_review/show.html')
    config.add_view('.views.OrderReviewView', request_type='altair.mobile.interfaces.IMobileRequest', route_name='order_review.show',
                    attr='post', request_method='POST', renderer='base/mobile/order_review/show.html')

    config.add_view('.views.order_review_form_view', name='order_review_form', renderer='base/pc/order_review/form.html')
    config.add_view('.views.order_review_form_view', name='order_review_form', renderer='base/mobile/order_review/form.html', request_type='altair.mobile.interfaces.IMobileRequest')

    config.add_view('.views.contact_view', route_name='contact', renderer='base/pc/static/contact.html')
    config.add_view('.views.contact_view', route_name='contact', renderer='base/mobile/static/contact.html', request_type='altair.mobile.interfaces.IMobileRequest')

def setup_plugins_views(config):
    PAYMENT_PLUGIN_ID_SEJ = 3
    PAYMENT_PLUGIN_ID_CARD = 1

    config.add_view('altair.app.ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_SEJ,
                    renderer='base/pc/cart/sej_payment_complete.html')
    config.add_view('altair.app.ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_SEJ, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer='base/mobile/cart/sej_payment_complete.html')

    config.add_view('altair.app.ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_CARD,
                    renderer='base/pc/cart/multicheckout_payment_complete.html')
    config.add_view('altair.app.ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID_CARD, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer='base/mobile/cart/multicheckout_payment_complete.html')

def setup_order_product_attribute_metadata(config):
    from altair.app.ticketing.orders.api import get_ordered_product_metadata_provider_registry
    from .metadata import metadata_provider
    get_ordered_product_metadata_provider_registry(config.registry).registerProvider(metadata_provider)
    
def includeme(config):
    config.include(setup_cart)
    config.include('altair.mobile')
    config.include(setup_views)
    config.include(setup_excviews)
    config.include(setup_plugins_views)

    config.include('altair.app.ticketing.orders')
    config.include(setup_order_product_attribute_metadata)

    config.include('.89ers')
    config.include('.bambitious')
