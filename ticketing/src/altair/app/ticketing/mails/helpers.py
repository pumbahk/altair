# coding=utf-8
import functools

from pyramid.view import render_view_to_response
from markupsafe import Markup
from altair.app.ticketing.core.models import PointUseTypeEnum
import logging
logger = logging.getLogger(__name__)


def build_delivery_viewlet(faildefault=None, message=None):
    message = message or "*viewlet mail*: %s is not found"
    def fn(request, *args, **kwargs):
        context = request.context
        plugin_id = context.payment_delivery_method_pair.delivery_method.delivery_plugin_id
        logger.debug("plugin_id:%s" % plugin_id)
        response = render_view_to_response(context, request, name="delivery-%s" % plugin_id, secure=False)
        if response is None:
            logger.debug(message % ("delivery-%s" % plugin_id))
            return faildefault
        return Markup(response.text)
    return fn

def build_payment_viewlet(faildefault=None, message=None):
    message = message or "*viewlet mail*: %s is not found"
    def fn(request, order=None, *args, **kwargs):
        context = request.context
        if order is not None and order.point_use_type is PointUseTypeEnum.AllUse:
            # 全額ポイント払いの場合は表示なし
            logger.info("This order has been paid by all points in full amount, "
                        "so payment viewlet to display is nothing.")
            return Markup()
        else:
            plugin_id = context.payment_delivery_method_pair.payment_method.payment_plugin_id
            logger.debug("plugin_id:%s" % plugin_id)
            response = render_view_to_response(context, request, name="payment-%s" % plugin_id, secure=False)
            if response is None:
                logger.debug(message % ("payment-%s" % plugin_id))
                return faildefault
            return Markup(response.text)
    return fn

render_delivery_finished_mail_viewlet = build_delivery_viewlet(faildefault="", message="*complete mail*: %s is not found")
render_payment_finished_mail_viewlet = build_payment_viewlet(faildefault="", message="*complete mail*: %s is not found")
render_delivery_cancel_mail_viewlet = build_delivery_viewlet(faildefault="", message="*cancel mail*: %s is not found")
render_payment_cancel_mail_viewlet = build_payment_viewlet(faildefault="", message="*cancel mail*: %s is not found")

## lots
render_delivery_lots_accepted_mail_viewlet = build_delivery_viewlet(faildefault="", message="*lots_accepted mail*: %s is not found")
render_payment_lots_accepted_mail_viewlet = build_payment_viewlet(faildefault="", message="*lots_accepted mail*: %s is not found")
render_delivery_lots_elected_mail_viewlet = build_delivery_viewlet(faildefault="", message="*lots_elected mail*: %s is not found")
render_payment_lots_elected_mail_viewlet = build_payment_viewlet(faildefault="", message="*lots_elected mail*: %s is not found")
render_delivery_lots_rejected_mail_viewlet = build_delivery_viewlet(faildefault="", message="*lots_rejected mail*: %s is not found")
render_payment_lots_rejected_mail_viewlet = build_payment_viewlet(faildefault="", message="*lots_rejected mail*: %s is not found")
