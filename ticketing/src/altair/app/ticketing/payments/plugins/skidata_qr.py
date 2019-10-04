# -*- coding:utf-8 -*-

from pyramid.response import Response
from altair.app.ticketing.payments.interfaces import IOrderDelivery
from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
)
from altair.pyramid_dynamic_renderer import lbr_view_config
from . import SKIDATA_QR_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.orders.models import OrderedProductItemToken
from altair.sqlahelper import get_db_session


def includeme(config):
    config.add_delivery_plugin(SkidataQRDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)


def _overridable(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID,
                     fallback_ua_type=fallback_ua_type)


@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID,
                 renderer=_overridable("skidata_qr_confirm.html"))
def deliver_confirm_viewlet(context, request):
    return dict()


@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID,
                 renderer=_overridable("skidata_qr_complete.html"))
def deliver_completion_viewlet(context, request):
    barcode_list = SkidataBarcode.find_all_by_order_no(context.order.order_no, get_db_session(request, name='slave'))
    return dict(barcode_list=barcode_list)


@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID,
                 renderer=_overridable("skidata_qr_mail_complete.html", fallback_ua_type='mail'))
@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID,
                 renderer=_overridable("skidata_qr_mail_complete.html", fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    return dict()


@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u"")


class SkidataQRDeliveryPlugin(object):
    def validate_order(self, request, order_like, update=False):
        pass

    def validate_order_cancellation(self, request, order, now):
        pass

    def prepare(self, request, cart):
        pass

    def finish(self, request, cart):
        """
        予約確定処理を実施する。
        SkidataBarcodeデータを新規に生成する。
        対象公演が当日の場合、SKIDATAとWhitelist連携を実施する
        :param request: リクエスト
        :param cart:  カート
        """
        # TODO 試合当日はSKIDATAと連携
        opi_tokens = OrderedProductItemToken.find_all_by_order_no(cart.order_no)
        for token in opi_tokens:
            SkidataBarcode.insert_new_barcode_by_token(token)

    def finish2(self, request, order_like):
        pass

    def finished(self, request, order):
        pass

    def refresh(self, request, order):
        pass

    def cancel(self, request, order, now=None):
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {}

