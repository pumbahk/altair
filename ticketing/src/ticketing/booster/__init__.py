from ticketing.payments.exceptions import PaymentPluginException
from pyramid.httpexceptions import HTTPNotFound
from ticketing.payments.interfaces import IOrderPayment

def setup_cart(config):
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')
    config.include('ticketing.cart')
    config.scan('ticketing.cart.views')
    config.add_subscriber('.api.on_order_completed', 'ticketing.cart.events.OrderCompleted')
    config.commit()

def setup_excviews(config):
    config.add_view('.excviews.OutTermSalesView', attr='pc', context='ticketing.cart.exceptions.OutTermSalesException', renderer='carts/out_term_sales.html')
    config.add_view('.excviews.OutTermSalesView', attr='mobile', context='ticketing.cart.exceptions.OutTermSalesException', renderer='carts_mobile/out_term_sales.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.notfound_view', context=HTTPNotFound, renderer="errors/not_found.html", )
    config.add_view('.excviews.notfound_view', context=HTTPNotFound,  renderer="errors_mobile/not_found.html", request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.forbidden_view', context="pyramid.httpexceptions.HTTPForbidden", renderer="errors/not_found.html", )
    config.add_view('.excviews.forbidden_view', context="pyramid.httpexceptions.HTTPForbidden", renderer="errors_mobile/not_found.html", request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors/error.html')
    config.add_view('.excviews.cart_creation_exception', context=PaymentPluginException, renderer='ticketing.cart:templates/errors_mobile/error.html', request_type='altair.mobile.interfaces.IMobileRequest')
    config.add_view('.excviews.exception_view',  context=StandardError, renderer="errors/error.html")
    config.add_view('.excviews.exception_view', context=StandardError,  renderer="errors_mobile/error.html", request_type='altair.mobile.interfaces.IMobileRequest')
    ## xxxx
    config.add_view('.excviews.exception_view', context=Exception, renderer="errors/not_found.html", )
    config.add_view('.excviews.exception_view', context=Exception, renderer="errors_mobile/not_found.html", request_type='altair.mobile.interfaces.IMobileRequest')

def setup_plugins_views(config):
    PAYMENT_PLUGIN_ID_SEJ = 3
    PAYMENT_PLUGIN_ID_CARD = 1

    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ,
                    renderer='carts/sej_payment_complete.html')
    config.add_view('ticketing.payments.plugins.sej.sej_payment_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_SEJ, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/sej_payment_complete.html")

    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD,
                    renderer='carts/multicheckout_payment_complete.html')
    config.add_view('ticketing.payments.plugins.multicheckout.completion_viewlet', context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID_CARD, request_type='altair.mobile.interfaces.IMobileRequest',
                    renderer="carts_mobile/multicheckout_payment_complete.html")

    
