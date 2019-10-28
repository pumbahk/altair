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
        """
        予約更新に伴う処理を実施する。
        予約更新によるSkidataBarcode.ordered_product_item_tokenの更新や、バーコードの追加・削除などを実施する。
        :param request: リクエスト
        :param order: 更新後の予約データ
        """
        barcode_and_token_to_update = list()  # 既存のSkidataBarcodeにひもづくOrderedProductItemTokenを更新するためのリスト
        barcode_list_to_cancel = list()  # 予約更新で削除されたSkidataBarcodeを削除するためのリスト
        tokens_to_add_barcode = list()  # 予約更新で追加されたOrderedProductItemTokenにSkidataBarcodeを追加するためのリスト

        # SkidataBarcodeはこの時点で更新前の予約に紐づいているのでslave_sessionから取得する
        # DBSessionだと前処理により同トランザクション内で予約が更新されており、更新前予約は論理削除されている
        existing_barcode_list = \
            SkidataBarcode.find_all_by_order_no(order.order_no, session=get_db_session(request, name='slave'))
        new_opi_tokens = OrderedProductItemToken.find_all_by_order_no(order.order_no)

        for existing_barcode in existing_barcode_list:
            existing_token = existing_barcode.ordered_product_item_token
            equivalent_token = self._find_equivalent_token_from_list(existing_token, new_opi_tokens)
            if equivalent_token:
                barcode_and_token_to_update.append((existing_barcode, equivalent_token))
            else:
                barcode_list_to_cancel.append(existing_barcode)

        tokens_to_update_barcode = [token for _, token in barcode_and_token_to_update]
        for new_token in new_opi_tokens:
            if new_token not in tokens_to_update_barcode:  # 更新リストにない場合は、追加とみなす(商品明細追加や商品個数追加など)
                tokens_to_add_barcode.append(new_token)

        for barcode, token in barcode_and_token_to_update:  # SkidataBarcodeのordered_product_item_tokenの置き換え
            SkidataBarcode.update_token(barcode.id, token.id)
        for barcode in barcode_list_to_cancel:  # 予約更新後に存在しないバーコードをキャンセル
            SkidataBarcode.cancel(barcode.id)
        for token in tokens_to_add_barcode:  # 予約更新後に追加されたOrderedProductItemTokenにバーコードを付与
            SkidataBarcode.insert_new_barcode_by_token(token)

    def cancel(self, request, order, now=None):
        pass

    def refund(self, request, order, refund_record):
        pass

    def get_order_info(self, request, order):
        return {}

    @staticmethod
    def _find_equivalent_token_from_list(target_token, token_list):
        """
        リストから予約更新前後で等価となるOrderedProductItemTokenを取得する
        :param target_token: 対象のOrderedProductItemToken
        :param token_list: 検索対象のOrderedProductItemTokenのリスト
        :return: 予約更新前後で等価となるOrderedProductItemToken。存在しない場合はNone
        """
        is_quantity_only = target_token.item.product_item.product.seat_stock_type.quantity_only
        for token in token_list:
            if is_quantity_only \
                    and target_token.item.product_item.name == token.item.product_item.name \
                    and target_token.serial == token.serial:
                return token  # 数受けの場合は「商品明細名」と「シリアル」で等価とみなす
            if not is_quantity_only \
                    and target_token.item.product_item.name == token.item.product_item.name\
                    and target_token.seat is not None and token.seat is not None \
                    and target_token.seat.name == token.seat.name:
                return token  # 席ありの場合は「商品明細名」と「席名」で等価とみなす
