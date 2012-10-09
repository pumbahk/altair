import functools
from .resources import CompleteMailDelivery, CompleteMailPayment, OrderCancelMailDelivery, OrderCancelMailPayment
from pyramid.view import render_view_to_response
from markupsafe import Markup
import logging
logger = logging.getLogger(__name__)


def as_delivery_viewlet(faildefault=None, message=None):
    message = message or "*viewlet mail*: %s is not found"
    def _as_delivery_viewlet(fn):
        @functools.wraps(fn)
        def viewlet(request, order, *args):
            logger.debug("*" * 80)
            plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
            logger.debug("plugin_id:%s" % plugin_id)

            context = fn(request, order, *args)
            response = render_view_to_response(context, request, name="delivery-%s" % plugin_id, secure=False)
            if response is None:
                logger.debug(message % ("delivery-%s" % plugin_id))
                return faildefault
            return Markup(response.text)
        return viewlet
    return _as_delivery_viewlet

def as_payment_viewlet(faildefault=None, message=None):
    message = message or "*viewlet mail*: %s is not found"
    def _as_payment_viewlet(fn):
        @functools.wraps(fn)
        def viewlet(request, order, *args):
            logger.debug("*" * 80)
            plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
            logger.debug("plugin_id:%s" % plugin_id)

            context = fn(request, order, *args)
            response = render_view_to_response(context, request, name="payment-%s" % plugin_id, secure=False)
            if response is None:
                logger.debug(message % ("payment-%s" % plugin_id))
                return faildefault
            return Markup(response.text)
        return viewlet
    return _as_payment_viewlet

@as_delivery_viewlet(faildefault="", message="*complete mail*: %s is not found")
def render_delivery_finished_mail_viewlet(request, order):
    return CompleteMailDelivery(request, order)

@as_payment_viewlet(faildefault="", message="*complete mail*: %s is not found")
def render_payment_finished_mail_viewlet(request, order):
    return CompleteMailPayment(request, order)

@as_delivery_viewlet(faildefault="", message="*cancel mail*: %s is not found")
def render_delivery_cancel_mail_viewlet(request, order):
    return OrderCancelMailDelivery(request, order)

@as_payment_viewlet(faildefault="", message="*cancel mail*: %s is not found")
def render_payment_cancel_mail_viewlet(request, order):
    return OrderCancelMailPayment(request, order)

