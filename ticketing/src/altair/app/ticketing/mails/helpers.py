import functools
from .resources import PurchaseCompleteMailDelivery, PurchaseCompleteMailPayment, OrderCancelMailDelivery, OrderCancelMailPayment
from .resources import LotsAcceptedMailDelivery, LotsAcceptedMailPayment
from .resources import LotsElectedMailDelivery, LotsElectedMailPayment
from .resources import LotsRejectedMailDelivery, LotsRejectedMailPayment

from pyramid.view import render_view_to_response
from markupsafe import Markup
import logging
logger = logging.getLogger(__name__)


def get_pdmp_order(order):
    return order.payment_delivery_pair

def get_pdmp_lot_entry(lot_entry):
    return lot_entry.payment_delivery_method_pair

def as_delivery_viewlet(faildefault=None, message=None, get_pdmp=get_pdmp_order):
    message = message or "*viewlet mail*: %s is not found"
    def _as_delivery_viewlet(fn):
        @functools.wraps(fn)
        def viewlet(request, subject, *args):
            logger.debug("*" * 80)
            plugin_id = get_pdmp(subject).delivery_method.delivery_plugin_id
            logger.debug("plugin_id:%s" % plugin_id)

            context = fn(request, subject, *args)
            response = render_view_to_response(context, request, name="delivery-%s" % plugin_id, secure=False)
            if response is None:
                logger.debug(message % ("delivery-%s" % plugin_id))
                return faildefault
            return Markup(response.text)
        return viewlet
    return _as_delivery_viewlet

def as_payment_viewlet(faildefault=None, message=None, get_pdmp=get_pdmp_order):
    message = message or "*viewlet mail*: %s is not found"
    def _as_payment_viewlet(fn):
        @functools.wraps(fn)
        def viewlet(request, subject, *args):
            logger.debug("*" * 80)
            plugin_id = get_pdmp(subject).payment_method.payment_plugin_id
            logger.debug("plugin_id:%s" % plugin_id)

            context = fn(request, subject, *args)
            response = render_view_to_response(context, request, name="payment-%s" % plugin_id, secure=False)
            if response is None:
                logger.debug(message % ("payment-%s" % plugin_id))
                return faildefault
            return Markup(response.text)
        return viewlet
    return _as_payment_viewlet

@as_delivery_viewlet(faildefault="", message="*complete mail*: %s is not found")
def render_delivery_finished_mail_viewlet(request, order):
    return PurchaseCompleteMailDelivery(request, order)

@as_payment_viewlet(faildefault="", message="*complete mail*: %s is not found")
def render_payment_finished_mail_viewlet(request, order):
    return PurchaseCompleteMailPayment(request, order)

@as_delivery_viewlet(faildefault="", message="*cancel mail*: %s is not found")
def render_delivery_cancel_mail_viewlet(request, order):
    return OrderCancelMailDelivery(request, order)

@as_payment_viewlet(faildefault="", message="*cancel mail*: %s is not found")
def render_payment_cancel_mail_viewlet(request, order):
    return OrderCancelMailPayment(request, order)

## lots

@as_delivery_viewlet(faildefault="", message="*lots_accepted mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_delivery_lots_accepted_mail_viewlet(request, lot_entry):
    return LotsAcceptedMailDelivery(request, lot_entry)

@as_payment_viewlet(faildefault="", message="*lots_accepted mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_payment_lots_accepted_mail_viewlet(request, lot_entry):
    return LotsAcceptedMailPayment(request, lot_entry)

@as_delivery_viewlet(faildefault="", message="*lots_elected mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_delivery_lots_elected_mail_viewlet(request, lot_entry):
    return LotsElectedMailDelivery(request, lot_entry)

@as_payment_viewlet(faildefault="", message="*lots_elected mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_payment_lots_elected_mail_viewlet(request, lot_entry):
    return LotsElectedMailPayment(request, lot_entry)

@as_delivery_viewlet(faildefault="", message="*lots_rejected mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_delivery_lots_rejected_mail_viewlet(request, lot_entry):
    return LotsRejectedMailDelivery(request, lot_entry)

@as_payment_viewlet(faildefault="", message="*lots_rejected mail*: %s is not found", get_pdmp=get_pdmp_lot_entry)
def render_payment_lots_rejected_mail_viewlet(request, lot_entry):
    return LotsRejectedMailPayment(request, lot_entry)
