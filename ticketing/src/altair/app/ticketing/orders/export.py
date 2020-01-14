# -*- coding: utf-8 -*-

import os, sys
import logging
import tempfile
import pickle
from io import BytesIO
from datetime import date, datetime
from collections import OrderedDict, namedtuple

from paste.util.multidict import MultiDict
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.expression import and_, or_

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart.api import get_cart_setting
from altair.app.ticketing.cart.helpers import format_number as _format_number
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer
from altair.app.ticketing.core.models import (
    StockType,
    Stock,
    Product,
    ProductItem,
    Organization,
    ChannelEnum,
    EventSetting,
    PerformanceSetting,
    SalesSegmentKindEnum)
from altair.app.ticketing.sej.models import SejRefundTicket, SejTicket
from altair.app.ticketing.famiport.models import FamiPortOrder, FamiPortReceipt, FamiPortReceiptType
from altair.app.ticketing.orders.models import Order
from .api import get_order_attribute_pair_pairs

logger = logging.getLogger(__name__)


def format_number(value):
    return _format_number(float(value))

def _create_mailsubscription_cache(organization_id, session):
    D = dict()
    query = session.query(MailSubscription)\
        .filter(MailSubscription.segment_id == MailMagazine.id)\
        .filter(or_(MailSubscription.status == None, MailSubscription.status == MailSubscriptionStatus.Subscribed.v))
    if organization_id:
        query = query.filter(MailMagazine.organization_id == organization_id)
    for ms in query:
        D[ms.email] = True
    return D

def one_or_empty(b):
    return u'1' if b else u''

japanese_columns = {
    u'order.order_no': u'予約番号',
    u'order.status': u'ステータス',
    u'order.payment_status': u'決済ステータス',
    u'order.created_at': u'予約日時',
    u'order.paid_at': u'支払日時',
    u'order.delivered_at': u'配送日時',
    u'order.canceled_at': u'キャンセル日時',
    u'order.created_from_lot_entry.lot.name': u'抽選',
    u'order.total_amount': u'合計金額',
    u'order.transaction_fee': u'決済手数料',
    u'order.delivery_fee': u'配送手数料',
    u'order.system_fee': u'システム利用料',
    u'order.special_fee': u'特別手数料',
    u'order.margin': u'内手数料金額',
    u'order.total_amount_ordered_product': u'チケット代金',
    u'order.refund_total_amount': u'払戻合計金額',
    u'order.refund_transaction_fee': u'払戻決済手数料',
    u'order.refund_delivery_fee': u'払戻配送手数料',
    u'order.refund_system_fee': u'払戻システム利用料',
    u'order.refund_special_fee': u'払戻特別手数料',
    u'order.note': u'メモ',
    u'order.special_fee_name': u'特別手数料名',
    u'order.multicheckout_approval_no': u'マルチ決済受領番号',
    u'order.card_brand': u'カードブランド',
    u'order.card_ahead_com_code': u'仕向け先企業コード',
    u'order.card_ahead_com_name': u'仕向け先企業名',
    u'order.issuing_start_at': u'発券開始日時',
    u'order.issuing_end_at': u'発券期限',
    u'order.payment_start_at': u'支払開始日時',
    u'order.payment_due_at': u'支払期限',
    u'order.cart_setting_id': u'カート設定',
    u'order.type':u'予約タイプ',
    u'order.count':u'チケット枚数',
    u'order.printed_at':u'発券日時（予約単位）',
    #u'anshin_checkout.order_id': u'楽天ペイ 注文番号',
    #u'anshin_checkout.order_control_id': u'楽天ペイ 注文管理番号',
    #u'anshin_checkout.used_point': u'楽天ペイ 利用ポイント数',
    #u'anshin_checkout.sales_at': u'楽天ペイ 売上日時',
    u'sej_order.pay_store_name': u'SEJ払込店舗',
    u'sej_order.ticketing_store_name': u'SEJ引換店舗',
    u'sej_order.billing_number': u'SEJ払込票番号',
    u'sej_order.exchange_number': u'SEJ引換票番号',
    u'user_profile.last_name': u'姓',
    u'user_profile.first_name': u'名',
    u'user_profile.last_name_kana': u'姓(カナ)',
    u'user_profile.first_name_kana': u'名(カナ)',
    u'user_profile.nick_name': u'ニックネーム',
    u'shipping_address.sex': u'性別',
    u'membership.name': u'会員種別名',
    u'membergroup.name': u'会員グループ名',
    u'user_credential.authz_identifier': u'会員種別ID',
    u'user_point_account.account_number': u'ポイント口座番号',
    u'shipping_address.last_name': u'配送先姓',
    u'shipping_address.first_name': u'配送先名',
    u'shipping_address.last_name_kana': u'配送先姓(カナ)',
    u'shipping_address.first_name_kana': u'配送先名(カナ)',
    u'shipping_address.zip': u'郵便番号',
    u'shipping_address.country': u'国',
    u'shipping_address.prefecture': u'都道府県',
    u'shipping_address.city': u'市区町村',
    u'shipping_address.address_1': u'住所1',
    u'shipping_address.address_2': u'住所2',
    u'shipping_address.tel_1': u'電話番号1',
    u'shipping_address.tel_2': u'電話番号2',
    u'shipping_address.fax': u'FAX',
    u'shipping_address.email_1': u'メールアドレス1',
    u'shipping_address.email_2': u'メールアドレス2',
    u'shipping_address.birthday': u'生年月日',
    u'payment_method.name': u'決済方法',
    u'delivery_method.name': u'引取方法',
    u'event.title': u'イベント',
    u'event_setting.event_operator': u'イベント登録担当者',
    u'event_setting.sales_person': u'イベント営業担当者',
    u'performance.name': u'公演',
    u'performance.code': u'公演コード',
    u'performance.start_on': u'公演日',
    u'performance_setting.performance_operator': u'公演登録担当者',
    u'performance_setting.sales_person': u'公演営業担当者',
    u'venue.name': u'会場',
    u'ordered_product.price': u'商品単価',
    u'ordered_product.quantity': u'商品個数',
    u'ordered_product.refund_price': u'払戻商品単価',
    u'ordered_product.product.name': u'商品名',
    u'ordered_product.product.sales_segment.sales_segment_group.name': u'販売区分',
    u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
    u'ordered_product_item.product_item.name': u'商品明細名',
    u'ordered_product_item.price': u'商品明細単価',
    u'ordered_product_item.quantity': u'商品明細個数',
    u'ordered_product_item.refund_price': u'払戻商品明細単価',
    u'ordered_product_item.print_histories': u'発券作業者',
    u'ordered_product_item.printed_at':u'発券日時（座席単位）',
    u'used_discount_codes': u'クーポン・割引コード',
    u'mail_magazine.mail_permission': u'メールマガジン受信可否',
    u'seat.name': u'座席名',
    u'stock_holder.name': u'枠名',
    u'account.name': u'配券元',
    u'stock_type.name': u'席種',
    u'famiport_receipt_payment.reserve_number': u'FM払込票番号',
    u'famiport_receipt_ticketing.reserve_number': u'FM引換票番号',
    u'order.channel': u'チャネル',
    u'point_grant_setting.rate': u'ポイント付与料率',
    u'point_grant_setting.fixed': u'固定付与ポイント',
    u'point_grant_history_entry.amount': u'ポイント付与額',
    u'skidata_barcode.data': u'SKIDATA_QRデータ'
}

ordered_ja_col = OrderedDict([
    (u'order.order_no', u'予約番号'),
    (u'order.status', u'ステータス'),
    (u'order.payment_status', u'決済ステータス'),
    (u'order.created_at', u'予約日時'),
    (u'order.canceled_at', u'キャンセル日時'),
    (u'order.paid_at', u'支払日時'),
    (u'order.printed_at', u'発券日時（予約単位）'),
    (u'ordered_product_item.printed_at', u'発券日時（座席単位）'),
    (u'order.delivered_at', u'配送日時'),
    (u'ordered_product_item.print_histories', u'発券作業者'),
    (u'payment_method.name', u'決済方法'),
    (u'delivery_method.name', u'引取方法'),
    (u'order.issuing_start_at', u'発券開始日時'),
    (u'order.issuing_end_at', u'発券期限'),
    (u'order.payment_start_at', u'支払開始日時'),
    (u'order.payment_due_at', u'支払期限'),
    (u'sej_order.billing_number', u'SEJ払込票番号'),
    (u'sej_order.exchange_number', u'SEJ引換票番号'),
    (u'famiport_receipt_payment.reserve_number', u'FM払込票番号'),
    (u'famiport_receipt_ticketing.reserve_number', u'FM引換票番号'),
    (u'order.card_brand', u'カードブランド'),
    (u'order.card_ahead_com_code', u'仕向け先企業コード'),
    (u'order.card_ahead_com_name', u'仕向け先企業名'),
    (u'event.title', u'イベント'),
    (u'event_setting.event_operator', u'イベント登録担当者'),
    (u'event_setting.sales_person', u'イベント営業担当者'),
    (u'order.created_from_lot_entry.lot.name', u'抽選'),
    (u'performance.name', u'公演'),
    (u'performance.code', u'公演コード'),
    (u'performance.start_on', u'公演日'),
    (u'performance_setting.performance_operator', u'公演登録担当者'),
    (u'performance_setting.sales_person', u'公演営業担当者'),
    (u'venue.name', u'会場'),
    (u'ordered_product.product.sales_segment.sales_segment_group.name', u'販売区分'),
    (u'ordered_product.product.sales_segment.sales_segment_group.kind', u'販売種別'),
    (u'account.name', u'配券元'),
    (u'ordered_product.product.sales_segment.margin_ratio', u'販売手数料率'),
    (u'stock_type.name', u'席種'),
    (u'ordered_product.product.name', u'商品名'),
    (u'ordered_product.price', u'商品単価'),
    (u'ordered_product.quantity', u'商品個数'),
    (u'ordered_product_item.product_item.name', u'商品明細名'),
    (u'ordered_product_item.price', u'商品明細単価'),
    (u'ordered_product_item.quantity', u'商品明細個数'),
    (u'used_discount_codes', u'クーポン・割引コード'),
    (u'order.count', u'チケット枚数'),
    (u'seat.name', u'座席名'),
    (u'order.refund_total_amount', u'払戻合計金額'),
    (u'order.refund_transaction_fee', u'払戻決済手数料'),
    (u'order.refund_delivery_fee', u'払戻配送手数料'),
    (u'order.refund_system_fee', u'払戻システム利用料'),
    (u'order.refund_special_fee', u'払戻特別手数料'),
    (u'ordered_product.refund_price', u'払戻商品単価'),
    (u'ordered_product_item.refund_price', u'払戻商品明細単価'),
    (u'order.total_amount', u'合計金額'),
    (u'order.total_amount_ordered_product', u'チケット代金'),
    (u'order.transaction_fee', u'決済手数料'),
    (u'order.delivery_fee', u'配送手数料'),
    (u'order.system_fee', u'システム利用料'),
    (u'order.special_fee_name', u'特別手数料名'),
    (u'order.special_fee', u'特別手数料'),
    (u'order.margin', u'内手数料金額'),
    (u'membership.name', u'会員種別名'),
    (u'membergroup.name', u'会員グループ名'),
    (u'user_credential.authz_identifier', u'会員種別ID'),
    (u'user_credential.auth_identifier', u'OpenID'),
    (u'user_credential.easy_id', u'easy_id'),
    (u'user_profile.last_name', u'姓'),
    (u'user_profile.first_name', u'名'),
    (u'user_profile.last_name_kana', u'姓(カナ)'),
    (u'user_profile.first_name_kana', u'名(カナ)'),
    (u'user_profile.nick_name', u'ニックネーム'),
    (u'shipping_address.sex', u'性別'),
    (u'shipping_address.last_name', u'配送先姓'),
    (u'shipping_address.first_name', u'配送先名'),
    (u'shipping_address.last_name_kana', u'配送先姓(カナ)'),
    (u'shipping_address.first_name_kana', u'配送先名(カナ)'),
    (u'shipping_address.zip', u'郵便番号'),
    (u'shipping_address.country', u'国'),
    (u'shipping_address.prefecture', u'都道府県'),
    (u'shipping_address.city', u'市区町村'),
    (u'shipping_address.address_1', u'住所1'),
    (u'shipping_address.address_2', u'住所2'),
    (u'shipping_address.tel_1', u'電話番号1'),
    (u'shipping_address.tel_2', u'電話番号2'),
    (u'shipping_address.fax', u'FAX'),
    (u'shipping_address.email_1', u'メールアドレス1'),
    (u'shipping_address.email_2', u'メールアドレス2'),
    (u'shipping_address.birthday', u'生年月日'),
    (u'mail_magazine.mail_permission', u'メールマガジン受信可否'),
    (u'user_point_account.account_number', u'ポイント口座番号'),
    (u'order.note', u'メモ'),
    (u'sej_order.ticketing_store_name', u'SEJ引換店舗'),
    (u'sej_order.pay_store_name', u'SEJ払込店舗'),
    (u'order.multicheckout_approval_no', u'マルチ決済受領番号'),
    (u'order.cart_setting_id', u'カート設定'),
    (u'order.type', u'予約タイプ'),
    (u'stock_holder.name', u'枠名'),
    (u'order.channel', u'チャネル'),
    (u'point_grant_setting.rate', u'ポイント付与料率'),
    (u'point_grant_setting.fixed', u'固定付与ポイント'),
    (u'point_grant_history_entry.amount', u'ポイント付与額'),
    (u'order.point_amount', u'利用ポイント'),
    (u'refund_point_entry.refund_point_amount', u'払戻付与ポイント'),
    (u'skidata_qr', u'SKIDATA QR')
])

def get_japanese_columns(request):
    return dict(japanese_columns)

def get_ordered_ja_col():
    return ordered_ja_col

class MarginRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        order = dereference(record, self.key)
        rendered_value = 0
        for ordered_product in order.ordered_products:
            margin = (ordered_product.product.sales_segment.margin_ratio / 100) if ordered_product.product.sales_segment is not None else 0
            rendered_value += (ordered_product.price * ordered_product.quantity) * margin
        return [
            ((u"", self.column_name, u""), unicode(rendered_value))
        ]

class CartSettingRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        cart_setting_id = dereference(record, self.key)

        if not cart_setting_id:
            cart_setting_id = record['organization'].setting.cart_setting_id
        cart_setting = get_cart_setting(context.request, cart_setting_id, session=context.session)
        if cart_setting is not None:
            rendered_value = cart_setting.name
        else:
            rendered_value = u''
        return [
            (
                (u"", self.column_name, u""),
                rendered_value
                )
            ]

class PerSeatQuantityRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        ordered_product_item = dereference(record, self.key)
        if ordered_product_item.seats:
            rendered_value = u"1"
        else:
            rendered_value = unicode(ordered_product_item.quantity)
        return [
            (
                (u"", self.column_name, u""),
                rendered_value
                )
            ]

class MailMagazineSubscriptionStateRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        emails = dereference(record, self.key, True) or []
        return [
            (
                (u"", self.column_name, u""),
                one_or_empty(any(context.mailsubscription_cache.get(email, False) for email in emails))
                )
            ]

class CurrencyRenderer(SimpleRenderer):
    def __call__(self, record, context):
        return [
            ((u'', self.name, u''), unicode(format_number(dereference(record, self.key))))
            ]


class ChannelRenderer(SimpleRenderer):
    def __call__(self, record, context):
        for channel in ChannelEnum:
            if channel.v == dereference(record, self.key):
                return [
                    ((u'', self.name, u''), channel.k)
                ]


class ZipRenderer(SimpleRenderer):
    def __call__(self, record, context):
        zip = dereference(record, self.key, True)
        zip = ('%s-%s' % (zip[0:3], zip[3:])) if zip else ''
        return [
            ((u'', self.name, u''), zip)
        ]

class SegmentGroupKindRenderer(SimpleRenderer):
    def __call__(self, record, context):
        for i, kind in enumerate(SalesSegmentKindEnum.order.v):
            if kind == dereference(record, self.key):
                kindname = getattr(SalesSegmentKindEnum, kind, None)
                return [
                    ((u'', self.name, u''), kindname.v)
                ]

class PrintHistoryRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        ordered_product_item = dereference(record, self.key)
        return [
            (
                (u"", self.column_name, u""),
                u", ".join(list(OrderedDict([(print_history.operator.name, True) for print_history in ordered_product_item.print_histories if print_history.operator is not None])))
                )
            ]

class DiscountCodeRendererByOrder(SimpleRenderer):
    def __call__(self, record, context):
        ordered_product_item = dereference(record, self.key)
        code_str = u','.join([used_discount_code.code for used_discount_code in ordered_product_item.used_discount_codes])
        return [((u'', self.name, u''), code_str)]

class DiscountCodeRendererBySeat(SimpleRenderer):
    def __call__(self, record, context):
        used_discount_codes = dereference(record, self.key)
        code_str = u','.join([used_discount_code.code for used_discount_code in used_discount_codes])
        return [((u'', self.name, u''), code_str)]

def attribute_coerce(value):
    if value is None:
        return u""
    elif isinstance(value, basestring):
        return value
    elif isinstance(value, (int, long, float)):
        return unicode(value)
    elif isinstance(value, datetime):
        return u"{0.year:04d}-{0.month:02d}-{0.day:02d} {0.hour:02d}:{0.minute:02d}:{0.second:02d}".format(value)
    elif isinstance(value, date):
        return u"{0.year:04d}-{0.month:02d}-{0.day:02d}".format(value)
    else:
        i = None
        try:
            i = iter(value)
        except TypeError:
            pass
        if i is not None:
            return u','.join(i)
    return '?'

class OrderAttributeRenderer(object):
    def __init__(self, key, variable_name, renderer_class=PlainTextRenderer):
        self.key = key
        self.variable_name = variable_name
        self.renderer_class = renderer_class

    def __call__(self, record, context):
        order = dereference(record, self.key)
        retval = []
        for (attr_key, attr_value), _ in get_order_attribute_pair_pairs(context.request, order, include_undefined_items=True, mode='any'):
            renderer = self.renderer_class(u'_', u'%s[%s]' % (self.variable_name, attr_key))
            attr_value = attribute_coerce(attr_value)
            retval.extend(renderer(dict(_=attr_value), context))
        return retval


class TotalAmountOrderedProductRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record, context):
        order = dereference(record, self.key)
        rendered_value = 0
        for ordered_product in order.ordered_products:
            rendered_value += (ordered_product.price * ordered_product.quantity)
        return [
            ((u"", self.column_name, u""), unicode(rendered_value))
        ]

class CSVRendererWrapper(object):
    def __init__(self, renderer, temporary_file_factory, writer_factory, marshaller_factory, records, localized_columns={}, block_size=131072):
        self.renderer = renderer
        self.temporary_file_factory = temporary_file_factory
        self.writer_factory = writer_factory
        self.marshaller_factory = marshaller_factory
        self.records = records
        self.localized_columns = localized_columns
        self.tf = None
        self.block_size = block_size

    def _write_rows_to_temp_file(self):
        if self.tf is None: 
            tf = self.temporary_file_factory()
            tfw = self.marshaller_factory.make_marshal(tf)
            for record in self.records:
                tfw(self.renderer.to_intermediate_repr(record))
            tf.seek(0, os.SEEK_SET)
            self.tf = tf

    def __iter__(self):
        try:
            self._write_rows_to_temp_file()
            bio = BytesIO()
            fw = self.writer_factory(bio)
            fw(self.renderer.render_header(self.localized_columns))
            yield bio.getvalue()
            tfr = self.marshaller_factory.make_unmarshal(self.tf)
            bio.seek(0)
            bio.truncate(0)
            for irow in tfr():
                fw(self.renderer.render_intermediate_repr(irow))
                if bio.tell() >= self.block_size:
                    retval = bio.getvalue()
                    bio.seek(0)
                    bio.truncate(0)
                    yield retval
            if bio.tell() > 0:
                yield bio.getvalue()
        except Exception as e:
            logger.exception(u'error occured during sending CSV data: {}'.format(e.message))
        finally:
            self.close()

    def close(self):
        if self.tf is not None:
            self.tf.close()
            self.tf = None


class PickleMarshallerFactory(object):
    def __init__(self):
        pass

    def make_marshal(self, f):
        return lambda d: pickle.dump(d, f)

    def make_unmarshal(self, f):
        def _():
            try:
                while True:
                    yield pickle.load(f)
            except EOFError:
                pass
        return _


class OrderCSV(object):
    EXPORT_TYPE_ORDER = 1
    EXPORT_TYPE_SEAT = 2

    common_columns_pre = [
        PlainTextRenderer(u'order.order_no'),
        PlainTextRenderer(u'order.status'),
        PlainTextRenderer(u'order.payment_status'),
        PlainTextRenderer(u'order.created_at'),
        PlainTextRenderer(u'order.paid_at'),
        PlainTextRenderer(u'order.delivered_at'),
        PlainTextRenderer(u'order.canceled_at'),
        PlainTextRenderer(u'order.created_from_lot_entry.lot.name'),
        CurrencyRenderer(u'order.total_amount'),
        CurrencyRenderer(u'order.transaction_fee'),
        CurrencyRenderer(u'order.delivery_fee'),
        CurrencyRenderer(u'order.system_fee'),
        CurrencyRenderer(u'order.special_fee'),
        MarginRenderer(u'order', u'order.margin'),
        CurrencyRenderer(u'order.refund_total_amount'),
        CurrencyRenderer(u'order.refund_transaction_fee'),
        CurrencyRenderer(u'order.refund_delivery_fee'),
        CurrencyRenderer(u'order.refund_system_fee'),
        CurrencyRenderer(u'order.refund_special_fee'),
        PlainTextRenderer(u'order.note'),
        PlainTextRenderer(u'order.special_fee_name'),
        PlainTextRenderer(u'order.card_brand'),
        PlainTextRenderer(u'order.card_ahead_com_code'),
        PlainTextRenderer(u'order.card_ahead_com_name'),
        PlainTextRenderer(u'order.issuing_start_at'),
        PlainTextRenderer(u'order.issuing_end_at'),
        PlainTextRenderer(u'order.payment_start_at'),
        PlainTextRenderer(u'order.payment_due_at'),
        PlainTextRenderer(u'sej_order.billing_number'),
        PlainTextRenderer(u'sej_order.exchange_number'),
        MailMagazineSubscriptionStateRenderer(
            u'shipping_address.emails',
            u'mail_magazine.mail_permission'
            ),
        PlainTextRenderer(u'user_profile.last_name'),
        PlainTextRenderer(u'user_profile.first_name'),
        PlainTextRenderer(u'user_profile.last_name_kana'),
        PlainTextRenderer(u'user_profile.first_name_kana'),
        PlainTextRenderer(u'user_profile.nick_name'),
        PlainTextRenderer(u'shipping_address.sex'),
        PlainTextRenderer(u'membership.name'),
        PlainTextRenderer(u'membergroup.name'),
        PlainTextRenderer(u'user_credential.authz_identifier'),
        PlainTextRenderer(u'shipping_address.last_name'),
        PlainTextRenderer(u'shipping_address.first_name'),
        PlainTextRenderer(u'shipping_address.last_name_kana'),
        PlainTextRenderer(u'shipping_address.first_name_kana'),
        ZipRenderer(u'shipping_address.zip'),
        PlainTextRenderer(u'shipping_address.country'),
        PlainTextRenderer(u'shipping_address.prefecture'),
        PlainTextRenderer(u'shipping_address.city'),
        PlainTextRenderer(u'shipping_address.address_1'),
        PlainTextRenderer(u'shipping_address.address_2'),
        PlainTextRenderer(u'shipping_address.tel_1', fancy=True),
        PlainTextRenderer(u'shipping_address.tel_2', fancy=True),
        PlainTextRenderer(u'shipping_address.fax', fancy=True),
        PlainTextRenderer(u'shipping_address.email_1'),
        PlainTextRenderer(u'shipping_address.email_2'),
        PlainTextRenderer(u'payment_method.name'),
        PlainTextRenderer(u'delivery_method.name'),
        PlainTextRenderer(u'event.title'),
        PlainTextRenderer(u'performance.name'),
        PlainTextRenderer(u'performance.code'),
        PlainTextRenderer(u'performance.start_on'),
        PlainTextRenderer(u'venue.name'),
        # CartSettingRenderer(u'order.cart_setting_id'),
        ]

    per_order_columns = \
        common_columns_pre + \
        [
            CollectionRenderer(
                u'ordered_products',
                u'ordered_product',
                [
                    CurrencyRenderer(u'ordered_product.price'),
                    PlainTextRenderer(u'ordered_product.quantity'),
                    CurrencyRenderer(u'ordered_product.refund_price'),
                    PlainTextRenderer(u'ordered_product.product.name'),
                    PlainTextRenderer(u'ordered_product.product.sales_segment.sales_segment_group.name'),
                    PlainTextRenderer(u'ordered_product.product.sales_segment.margin_ratio'),
                    ]
                ),
            CollectionRenderer(
                u'ordered_products',
                u'ordered_product',
                [
                    CollectionRenderer(
                        u'ordered_product.ordered_product_items',
                        u'ordered_product_item',
                        [
                            PlainTextRenderer(u'ordered_product_item.product_item.name'),
                            CurrencyRenderer(u'ordered_product_item.price'),
                            PlainTextRenderer(u'ordered_product_item.quantity'),
                            CurrencyRenderer(u'ordered_product_item.refund_price'),
                            PrintHistoryRenderer(u'ordered_product_item', u'ordered_product_item.print_histories'),
                            ]
                        ),
                    ]
                ),
            CollectionRenderer(
                u'ordered_products',
                u'ordered_product',
                [
                    CollectionRenderer(
                        u'ordered_product.ordered_product_items',
                        u'ordered_product_item',
                        [
                            CollectionRenderer(
                                u'ordered_product_item.seats',
                                u'seat',
                                [
                                    PlainTextRenderer(u'seat.name'),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            CollectionRenderer(
                u'ordered_products',
                u'ordered_product',
                [
                    CollectionRenderer(
                        u'ordered_product.ordered_product_items',
                        u'ordered_product_item',
                        [
                            AttributeRenderer(
                                u'ordered_product_item.attributes',
                                u'attribute'
                                ),
                            ]
                        ),
                    ]
                ),
            OrderAttributeRenderer(
                u'order',
                u'attribute'
                ),
            ]

    per_seat_columns = \
        common_columns_pre + \
        [
            CurrencyRenderer(u'ordered_product.price'),
            PlainTextRenderer(u'ordered_product.quantity'),
            CurrencyRenderer(u'ordered_product.refund_price'),
            PlainTextRenderer(u'ordered_product.product.name'),
            PlainTextRenderer(u'ordered_product.product.sales_segment.sales_segment_group.name'),
            PlainTextRenderer(u'ordered_product_item.product_item.name'),
            CurrencyRenderer(u'ordered_product_item.price'),
            PerSeatQuantityRenderer(u'ordered_product_item', u'ordered_product_item.quantity'),
            CurrencyRenderer(u'ordered_product_item.refund_price'),
            PrintHistoryRenderer(u'ordered_product_item', u'ordered_product_item.print_histories'),
            PlainTextRenderer(u'seat.name'),
            PlainTextRenderer(u'stock_holder.name'),
            AttributeRenderer(
                u'ordered_product_item.attributes',
                u'attribute'
                ),
            OrderAttributeRenderer(
                u'order',
                u'attribute'
                ),
            ]

    def __init__(self, request, export_type=EXPORT_TYPE_ORDER, organization_id=None, localized_columns={},
                 excel_csv=False, session=DBSession, empty_columns=None):
        self.request = request
        self.export_type = export_type
        column_renderers = None
        if export_type == self.EXPORT_TYPE_ORDER:
            column_renderers = self.per_order_columns
        elif export_type == self.EXPORT_TYPE_SEAT:
            column_renderers = self.per_seat_columns
        if column_renderers is None:
            raise ValueError('export_type')

        self._apply_empty_renderer(column_renderers, empty_columns)
        self.column_renderers = column_renderers
        self.enable_fancy = excel_csv
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.localized_columns = localized_columns
        self.session = session
        self.organization = session.query(Organization).filter_by(id=self.organization_id).one()
        self.marshaller_factory = PickleMarshallerFactory()

    def _apply_empty_renderer(self, columns, empty_targets=None):
        """対象のカラムを値を空で表示します"""
        if type(empty_targets) not in (list, tuple):
            return

        # CSVにセットされる値を空に置き換えるRendererクラスを適用します
        class EmptyTextRenderer(SimpleRenderer):
            def __call__(self, record, context):
                return [((u'', self.name, u''), u'')]

        for idx, val in enumerate(columns):
            if isinstance(val, SimpleRenderer) and val.key in empty_targets:
                columns[idx] = EmptyTextRenderer(val.key)

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id, self.session)
        return self._mailsubscription_cache

    def iter_records_for_order(self, order):
        user_credential = order.user.user_credential if order.user else None
        member = order.user.member if order.user and order.user.member else None
        common_record = {
            u'order': order,
            u'sej_order': order.sej_order if order.sej_order else None,
            u'user_profile': order.user.user_profile if order.user else None,
            u'membership': order.membership,
            u'membergroup': order.membergroup,
            u'user_credential': user_credential,
            u'shipping_address': order.shipping_address,
            u'payment_method': order.payment_delivery_pair.payment_method,
            u'delivery_method': order.payment_delivery_pair.delivery_method,
            u'organization': self.organization, # XXX
            u'event': order.performance.event,
            u'performance': order.performance,
            u'venue': order.performance.venue,
            }
        if self.export_type == self.EXPORT_TYPE_ORDER:
            record = dict(common_record)
            record[u'ordered_products'] = order.ordered_products
            yield record
        elif self.export_type == self.EXPORT_TYPE_SEAT:
            for ordered_product in order.ordered_products:
                for ordered_product_item in ordered_product.ordered_product_items:
                    if ordered_product_item.seats:
                        for seat in ordered_product_item.seats:
                            record = dict(common_record)
                            record[u'seat'] = seat
                            record[u'stock_holder'] = ordered_product_item.product_item.stock.stock_holder
                            record[u'ordered_product_item'] = ordered_product_item
                            record[u'ordered_product'] = ordered_product
                            yield record
                    else:
                        record = dict(common_record)
                        record[u'seat'] = None
                        record[u'ordered_product_item'] = ordered_product_item
                        record[u'ordered_product'] = ordered_product
                        yield record
        else:
            raise ValueError(self.export_type)

    def __call__(self, orders, writer_factory):
        return CSVRendererWrapper(
            renderer=CSVRenderer(self.column_renderers, self),
            temporary_file_factory=lambda: tempfile.SpooledTemporaryFile(max_size=16777216),
            writer_factory=writer_factory,
            marshaller_factory=self.marshaller_factory,
            records=(
                record
                for order in orders
                for record in self.iter_records_for_order(order)
                ),
            localized_columns=self.localized_columns
            )

class OrderOptionalCSV(object):
    EXPORT_TYPE_ORDER = 1
    EXPORT_TYPE_SEAT = 2

    common_candidates = {
        u'order.order_no': PlainTextRenderer(u'order.order_no'),
        u'order.status': PlainTextRenderer(u'order.status'),
        u'order.payment_status': PlainTextRenderer(u'order.payment_status'),
        u'order.created_at': PlainTextRenderer(u'order.created_at'),
        u'order.paid_at': PlainTextRenderer(u'order.paid_at'),
        u'order.delivered_at': PlainTextRenderer(u'order.delivered_at'),
        u'order.canceled_at': PlainTextRenderer(u'order.canceled_at'),
        u'order.created_from_lot_entry.lot.name': PlainTextRenderer(u'order.created_from_lot_entry.lot.name'),
        u'order.total_amount': CurrencyRenderer(u'order.total_amount'),
        u'order.transaction_fee': CurrencyRenderer(u'order.transaction_fee'),
        u'order.delivery_fee': CurrencyRenderer(u'order.delivery_fee'),
        u'order.system_fee': CurrencyRenderer(u'order.system_fee'),
        u'order.special_fee': CurrencyRenderer(u'order.special_fee'),
        u'order.margin': MarginRenderer(u'order', u'order.margin'),
        #u'order.total_amount_ordered_product': TotalAmountOrderedProductRenderer(u'order', u'order.total_amount_ordered_product'),
        # total amount of ordered product
        u'order.total_amount_ordered_product': {
            EXPORT_TYPE_ORDER: TotalAmountOrderedProductRenderer(u'order', u'order.total_amount_ordered_product'),

            # 座席単位：座席に紐づく商品明細の商品単価
            EXPORT_TYPE_SEAT: CurrencyRenderer(u'ordered_product_item.price')
        },
        u'order.refund_total_amount': CurrencyRenderer(u'order.refund_total_amount'),
        u'order.refund_transaction_fee': CurrencyRenderer(u'order.refund_transaction_fee'),
        u'order.refund_delivery_fee': CurrencyRenderer(u'order.refund_delivery_fee'),
        u'order.refund_system_fee': CurrencyRenderer(u'order.refund_system_fee'),
        u'order.refund_special_fee': CurrencyRenderer(u'order.refund_special_fee'),
        u'order.note': PlainTextRenderer(u'order.note'),
        u'order.special_fee_name': PlainTextRenderer(u'order.special_fee_name'),
        u'order.card_brand': PlainTextRenderer(u'order.card_brand'),
        u'order.card_ahead_com_code': PlainTextRenderer(u'order.card_ahead_com_code'),
        u'order.card_ahead_com_name': PlainTextRenderer(u'order.card_ahead_com_name'),
        u'order.issuing_start_at': PlainTextRenderer(u'order.issuing_start_at'),
        u'order.issuing_end_at': PlainTextRenderer(u'order.issuing_end_at'),
        u'order.payment_start_at': PlainTextRenderer(u'order.payment_start_at'),
        u'order.payment_due_at': PlainTextRenderer(u'order.payment_due_at'),
        u'order.printed_at':PlainTextRenderer(u'order.printed_at'),
        u'order.multicheckout_approval_no':PlainTextRenderer(u'order.multicheckout_approval_no'),
        u'order.point_amount': CurrencyRenderer(u'order.point_amount'),
        u'sej_order.billing_number': PlainTextRenderer(u'sej_order.billing_number'),
        u'sej_order.exchange_number': PlainTextRenderer(u'sej_order.exchange_number'),
        u'user_profile.last_name': PlainTextRenderer(u'user_profile.last_name'),
        u'user_profile.first_name': PlainTextRenderer(u'user_profile.first_name'),
        u'user_profile.last_name_kana': PlainTextRenderer(u'user_profile.last_name_kana'),
        u'user_profile.first_name_kana': PlainTextRenderer(u'user_profile.first_name_kana'),
        u'user_profile.nick_name': PlainTextRenderer(u'user_profile.nick_name'),
        u'shipping_address.sex': PlainTextRenderer(u'shipping_address.sex'),
        u'membership.name': PlainTextRenderer(u'membership.name'),
        u'membergroup.name': PlainTextRenderer(u'membergroup.name'),
        u'user_point_account.account_number': PlainTextRenderer(u'user_point_account.account_number'),
        u'user_credential.authz_identifier': PlainTextRenderer(u'user_credential.authz_identifier'),
        u'user_credential.auth_identifier': PlainTextRenderer(u'user_credential.auth_identifier'),
        u'user_credential.easy_id': PlainTextRenderer(u'user_credential.easy_id'),
        u'shipping_address.last_name': PlainTextRenderer(u'shipping_address.last_name'),
        u'shipping_address.first_name': PlainTextRenderer(u'shipping_address.first_name'),
        u'shipping_address.last_name_kana': PlainTextRenderer(u'shipping_address.last_name_kana'),
        u'shipping_address.first_name_kana': PlainTextRenderer(u'shipping_address.first_name_kana'),
        u'shipping_address.zip': ZipRenderer(u'shipping_address.zip'),
        u'shipping_address.country': PlainTextRenderer(u'shipping_address.country'),
        u'shipping_address.prefecture': PlainTextRenderer(u'shipping_address.prefecture'),
        u'shipping_address.city': PlainTextRenderer(u'shipping_address.city'),
        u'shipping_address.address_1': PlainTextRenderer(u'shipping_address.address_1'),
        u'shipping_address.address_2': PlainTextRenderer(u'shipping_address.address_2'),
        u'shipping_address.tel_1': PlainTextRenderer(u'shipping_address.tel_1', fancy=True),
        u'shipping_address.tel_2': PlainTextRenderer(u'shipping_address.tel_2', fancy=True),
        u'shipping_address.fax': PlainTextRenderer(u'shipping_address.fax', fancy=True),
        u'shipping_address.email_1': PlainTextRenderer(u'shipping_address.email_1'),
        u'shipping_address.email_2': PlainTextRenderer(u'shipping_address.email_2'),
        u'shipping_address.birthday': PlainTextRenderer(u'shipping_address.birthday'),
        u'payment_method.name': PlainTextRenderer(u'payment_method.name'),
        u'delivery_method.name': PlainTextRenderer(u'delivery_method.name'),
        u'event.title': PlainTextRenderer(u'event.title'),
        u'event_setting.event_operator': PlainTextRenderer(u'event_setting.event_operator'),
        u'event_setting.sales_person': PlainTextRenderer(u'event_setting.sales_person'),
        u'performance.name': PlainTextRenderer(u'performance.name'),
        u'performance.code': PlainTextRenderer(u'performance.code'),
        u'performance.start_on': PlainTextRenderer(u'performance.start_on'),
        u'performance_setting.performance_operator': PlainTextRenderer(u'performance_setting.performance_operator'),
        u'performance_setting.sales_person': PlainTextRenderer(u'performance_setting.sales_person'),
        u'venue.name': PlainTextRenderer(u'venue.name'),
        u'mail_magazine.mail_permission': MailMagazineSubscriptionStateRenderer(
        u'shipping_address.emails', u'mail_magazine.mail_permission'),
        u'account.name': PlainTextRenderer(u'account.name'),
        u'stock_type.name': PlainTextRenderer(u'stock_type.name'),
        u'famiport_receipt_payment.reserve_number': PlainTextRenderer(u'famiport_receipt_payment.reserve_number'),
        u'famiport_receipt_ticketing.reserve_number': PlainTextRenderer(u'famiport_receipt_ticketing.reserve_number'),
        u'order.channel': ChannelRenderer(u'order.channel'),
        u'point_grant_history_entry.amount': PlainTextRenderer(u'point_grant_history_entry.amount'),
        u'point_grant_setting.rate': PlainTextRenderer(u'point_grant_setting.rate'),
        u'point_grant_setting.fixed': PlainTextRenderer(u'point_grant_setting.fixed'),
        u'refund_point_entry.refund_point_amount': PlainTextRenderer(u'refund_point_entry.refund_point_amount'),
    }

    ordered_product_candidates ={
        u'ordered_product.price': CurrencyRenderer(u'ordered_product.price'),
        u'ordered_product.refund_price': CurrencyRenderer(u'ordered_product.refund_price'),
        u'ordered_product.product.name': PlainTextRenderer(u'ordered_product.product.name'),
        u'ordered_product.quantity': PlainTextRenderer(u'ordered_product.quantity'),

        u'ordered_product.product.sales_segment.sales_segment_group.name':
            PlainTextRenderer(u'ordered_product.product.sales_segment.sales_segment_group.name'),

        u'ordered_product.product.sales_segment.sales_segment_group.kind':
            SegmentGroupKindRenderer(u'ordered_product.product.sales_segment.sales_segment_group.kind'),

        u'ordered_product.product.sales_segment.margin_ratio':
            PlainTextRenderer(u'ordered_product.product.sales_segment.margin_ratio'),
    }

    ordered_product_item_candidates ={
        u'ordered_product_item.product_item.name': PlainTextRenderer(u'ordered_product_item.product_item.name'),
        u'ordered_product_item.price': CurrencyRenderer(u'ordered_product_item.price'),
        u'ordered_product_item.refund_price': CurrencyRenderer(u'ordered_product_item.refund_price'),
        u'ordered_product_item.printed_at': PlainTextRenderer(u'ordered_product_item.printed_at'),

        u'ordered_product_item.print_histories': PrintHistoryRenderer(u'ordered_product_item',
                                                                      u'ordered_product_item.print_histories'
                                                                      ),
        u'ordered_product_item.quantity': {
            EXPORT_TYPE_ORDER: PlainTextRenderer(u'ordered_product_item.quantity'),
            EXPORT_TYPE_SEAT: PerSeatQuantityRenderer(u'ordered_product_item', u'ordered_product_item.quantity')
        },
        # seat
        u'seat.name': {
            EXPORT_TYPE_ORDER:
                CollectionRenderer(u'ordered_product_item.seats', u'seat', [PlainTextRenderer(u'seat.name')]),

            EXPORT_TYPE_SEAT:
                PlainTextRenderer(u'seat.name')
        },

        # attribute
        u'attribute': AttributeRenderer(u'ordered_product_item.attributes', u'attribute'),

        # discount code
        u'used_discount_codes': {
            EXPORT_TYPE_ORDER:
                DiscountCodeRendererByOrder(u'ordered_product_item', u'used_discount_codes'),
            EXPORT_TYPE_SEAT:
                DiscountCodeRendererBySeat(u'used_discount_codes')
        },

        # SKIDATA QR
        u'skidata_qr': {
            EXPORT_TYPE_ORDER: CollectionRenderer(u'ordered_product_item.tokens', u'token', [
                PlainTextRenderer(u'token.skidata_barcode.data', name=u'skidata_qr')]),
            EXPORT_TYPE_SEAT: PlainTextRenderer(u'skidata_qr')
        }

    }

    def __init__(self, request, export_type=EXPORT_TYPE_ORDER, organization_id=None, localized_columns={}, excel_csv=False, session=None, option_columns=None):
        self.request = request
        self.export_type = export_type
        self.column_renderers = self.get_export_renderers(export_type, option_columns)
        self.enable_fancy = excel_csv
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.localized_columns = localized_columns
        self.session = session if session else get_db_session(request, 'slave')
        self.session_famiport = None
        self.organization = session.query(Organization).filter_by(id=self.organization_id).one()
        self.marshaller_factory = PickleMarshallerFactory()

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id, self.session)
        return self._mailsubscription_cache

    def _get_renderer(self, option, candidates, export_type):
        renderer = candidates.get(option, None)
        # レンダーがエクスポートタイプに紐づくことを確認
        if isinstance(renderer, dict):
            renderer = renderer.get(export_type, None)
        return renderer

    def get_export_renderers(self, export_type, option_columns):
        export_renderers = []

        if not option_columns:
            return export_renderers

        for option in option_columns:
            # 共通カラム

            if option in self.common_candidates:
                renderer = self._get_renderer(option, self.common_candidates, export_type)
            elif option in self.ordered_product_candidates:
                renderer = self._get_renderer(option, self.ordered_product_candidates, export_type)
                if renderer and export_type == self.EXPORT_TYPE_ORDER:
                    renderer = CollectionRenderer(u'ordered_products',u'ordered_product',[renderer])
            elif option in self.ordered_product_item_candidates:
                renderer = self._get_renderer(option, self.ordered_product_item_candidates, export_type)
                if renderer and export_type == self.EXPORT_TYPE_ORDER:
                    renderer = CollectionRenderer(
                        u'ordered_products',
                        u'ordered_product',
                        [CollectionRenderer(
                            u'ordered_product.ordered_product_items',
                            u'ordered_product_item',
                            [renderer]
                        )]
                    )
            else:
                # common_column、ordered_product_candidatesとordered_product_itemにない場合はワーニングを出す。
                logger.warning(msg=u'The column: {0} is not found!!'.format(option))
                renderer = None

            if renderer:
                export_renderers.append(renderer)

        return export_renderers

    # 予約に紐づくポイントインポート口座オブジェクトを取得
    def lookup_user_point_account(self, order):
        from altair.app.ticketing.orders.models import order_user_point_account_table
        from altair.app.ticketing.users.models import UserPointAccount

        query = self.session.query(UserPointAccount.account_number)\
            .join(order_user_point_account_table,
                  UserPointAccount.id == order_user_point_account_table.c.user_point_account_id)\
            .join(Order, order_user_point_account_table.c.order_id == Order.id)\
            .filter(Order.id == order.id)

        try:
            return query.one()
        except NoResultFound:
            return None

    # 予約に紐づくポイント付与額を取得
    def lookup_point_grant_history_entry(self, order):
        from altair.app.ticketing.loyalty.models import PointGrantHistoryEntry
        query = self.session.query(PointGrantHistoryEntry.amount) \
            .join(Order, PointGrantHistoryEntry.order_id == Order.id) \
            .filter(Order.id == order.id)
        try:
            return query.one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            return None

    def lookup_refund_point_entry(self, order):
        from altair.app.ticketing.orders.models import RefundPointEntry
        query = self.session.query(RefundPointEntry.refund_point_amount) \
            .join(Order, RefundPointEntry.order_no == Order.order_no) \
            .filter(Order.order_no == order.order_no) \
            .group_by(RefundPointEntry.order_no) \
            .order_by(RefundPointEntry.seq_no.desc())
        try:
            return query.one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            return None

    # 予約に紐づくポイント付与料率・固定付与ポイントを取得
    def lookup_point_grant_setting(self, order):
        from altair.app.ticketing.loyalty.models import PointGrantSetting, SalesSegment_PointGrantSetting
        query = self.session.query(PointGrantSetting.rate, PointGrantSetting.fixed) \
            .join(SalesSegment_PointGrantSetting,
                  SalesSegment_PointGrantSetting.c.point_grant_setting_id == PointGrantSetting.id) \
            .join(Order, Order.sales_segment_id == SalesSegment_PointGrantSetting.c.sales_segment_id) \
            .filter(Order.order_no == order.order_no, Order.created_at >= PointGrantSetting.start_at,
                    Order.created_at <= PointGrantSetting.end_at).order_by(Order.created_at.desc())

        point_grant_setting=query.first()
        if not point_grant_setting:
            from altair.app.ticketing.core.models import OrganizationSetting
            organization_setting = self.session.query(OrganizationSetting) \
                .filter(OrganizationSetting.organization_id == self.organization_id).one()
            _PointGrantSetting = namedtuple('_PointGrantSetting', ('rate', 'fixed'))
            return _PointGrantSetting (
                rate=organization_setting.point_rate if organization_setting.point_rate else None,
                fixed=organization_setting.point_fixed if organization_setting.point_fixed else None
            )
        return point_grant_setting


    # 決済方法か取引方法がファミポートの場合のみ情報を取得する。それ以外の場合はNoneを返す
    def lookup_famiport_receipt(self, order, payment_flag=False, ticketing_flag=False):
        if not payment_flag and not ticketing_flag:
            return None

        if not self.session_famiport:
            self.session_famiport = get_db_session(self.request, 'famiport_slave')

        query = self.session_famiport.query(FamiPortReceipt.reserve_number)\
                                     .join(FamiPortOrder)\
                                     .filter(FamiPortOrder.order_no == order.order_no)
        if payment_flag:
            query = query.filter(or_(FamiPortReceipt.type == FamiPortReceiptType.CashOnDelivery.value,
                                     FamiPortReceipt.type == FamiPortReceiptType.Payment.value))\
                         .order_by(FamiPortReceipt.created_at.desc())
        elif ticketing_flag:
            query = query.filter(or_(FamiPortReceipt.type == FamiPortReceiptType.CashOnDelivery.value,
                                     FamiPortReceipt.type == FamiPortReceiptType.Ticketing.value))\
                         .order_by(FamiPortReceipt.created_at.desc())
        else:
            logger.warning(u'lookup_famiport_receipt was not set to get either payment nor ticketing...')
            return None

        return query.first()

    def lookup_event_setting(self, e_id):
        try:
            es = self.session.query(EventSetting).filter_by(event_id=e_id).one()
            return es
        except NoResultFound:
            logger.exception(u'no event setting is found when download the order info.')
        except MultipleResultsFound:
            logger.exception(u'multiple event settings are found when download the order info.')
        return None

    def lookup_performance_setting(self, p_id):
        try:
            ps = self.session.query(PerformanceSetting).filter_by(performance_id=p_id).one()
            return ps
        except NoResultFound:
            logger.exception(u'no performance setting is found when download the order info.')
        except MultipleResultsFound:
            logger.exception(u'multiple performance settings are found when download the order info.')
        return None


    def iter_records_for_order(self, order):
        user_credential = order.user.user_credential if order.user else None

        user_point_account = self.lookup_user_point_account(order)
        point_grant_history_entry = self.lookup_point_grant_history_entry(order)
        point_grant_setting = self.lookup_point_grant_setting(order)
        famiport_receipt_payment = self.lookup_famiport_receipt(order, payment_flag=True)
        famiport_receipt_ticketing = self.lookup_famiport_receipt(order, ticketing_flag=True)
        event_setting = self.lookup_event_setting(order.performance.event.id)
        performance_setting = self.lookup_performance_setting(order.performance.id)
        refund_point_entry = self.lookup_refund_point_entry(order)

        common_record = {
            u'order': order,
            u'sej_order': order.sej_order if order.sej_order else None,
            u'user_profile': order.user.user_profile if order.user else None,
            u'membership': order.membership,
            u'membergroup': order.membergroup,
            u'user_credential': user_credential,
            u'shipping_address': order.shipping_address,
            u'payment_method': order.payment_delivery_pair.payment_method,
            u'delivery_method': order.payment_delivery_pair.delivery_method,
            u'organization': self.organization, # XXX
            u'event': order.performance.event,
            u'performance': order.performance,
            u'venue': order.performance.venue,
            u'user_point_account': user_point_account,
            u'stock_type': order.ordered_products[0].product.seat_stock_type if order.ordered_products[0] else None,
            u'account': order.performance.account,
            u'famiport_receipt_payment': famiport_receipt_payment,
            u'famiport_receipt_ticketing': famiport_receipt_ticketing,
            u'event_setting': event_setting,
            u'performance_setting': performance_setting,
            u'point_grant_history_entry': point_grant_history_entry,
            u'point_grant_setting': point_grant_setting,
            u'refund_point_entry': refund_point_entry
            }
        if self.export_type == self.EXPORT_TYPE_ORDER:
            record = dict(common_record)
            record[u'ordered_products'] = order.ordered_products
            yield record
        elif self.export_type == self.EXPORT_TYPE_SEAT:
            for ordered_product in order.ordered_products:
                for ordered_product_item in ordered_product.ordered_product_items:
                    if ordered_product_item.seats:
                        for token in ordered_product_item.tokens:
                            record = dict(common_record)
                            record[u'seat'] = token.seat
                            record[u'used_discount_codes'] = token.used_discount_codes
                            record[u'stock_holder'] = ordered_product_item.product_item.stock.stock_holder
                            record[u'ordered_product_item'] = ordered_product_item
                            record[u'ordered_product'] = ordered_product
                            record[u'skidata_qr'] = token.skidata_barcode.data if token.skidata_barcode else None
                            yield record
                    else:
                        record = dict(common_record)
                        record[u'seat'] = None
                        record[u'used_discount_codes'] = ordered_product_item.used_discount_codes
                        record[u'ordered_product_item'] = ordered_product_item
                        record[u'ordered_product'] = ordered_product
                        record[u'skidata_qr'] = \
                            ' '.join([token.skidata_barcode.data
                                      for token in ordered_product_item.tokens if token.skidata_barcode])
                        yield record
        else:
            raise ValueError(self.export_type)

    def __call__(self, orders, writer_factory):
        return CSVRendererWrapper(
            renderer=CSVRenderer(self.column_renderers, self),
            temporary_file_factory=lambda: tempfile.SpooledTemporaryFile(max_size=16777216),
            writer_factory=writer_factory,
            marshaller_factory=self.marshaller_factory,
            records=(
                record
                for order in orders
                for record in self.iter_records_for_order(order)
                ),
            localized_columns=self.localized_columns
            )


class RefundResultCSVExporter(object):
    csv_header = [
        ('order_no'            , u'予約番号'),
        ('stock_type_name'     , u'席種'),
        ('product_name'        , u'商品名'),
        ('product_item_name'   , u'商品明細名'),
        ('sent_at'             , u'データ送信日時'),
        ('refunded_at'         , u'コンビニ払戻日時'),
        ('barcode_number'      , u'バーコード番号'),
        ('refund_ticket_amount', u'払戻金額(チケット分)'),
        ('refund_other_amount' , u'払戻金額(手数料分)'),
        ('status'              , u'払戻状態')
        ]

    def __init__(self, session, refund):
        self.session = session
        self.refund = refund

    def __iter__(self):
        query = self.session.query(
            SejRefundTicket.order_no.label('order_no'),
            StockType.name.label('stock_type_name'),
            Product.name.label('product_name'),
            ProductItem.name.label('product_item_name'),
            SejRefundTicket.sent_at.label('sent_at'),
            SejRefundTicket.refunded_at.label('refunded_at'),
            SejRefundTicket.ticket_barcode_number.label('barcode_number'),
            SejRefundTicket.refund_ticket_amount.label('refund_ticket_amount'),
            SejRefundTicket.refund_other_amount.label('refund_other_amount'),
            SejRefundTicket.status.label('status'),
        ).join(
            Order, SejRefundTicket.order_no == Order.order_no
        ).join(
            SejTicket, SejTicket.barcode_number == SejRefundTicket.ticket_barcode_number
        ).join(
            ProductItem,
            Product,
            Stock,
            StockType
        ).filter(
            Order.refund_id == self.refund.id
        )

        for row in query:
            yield OrderedDict([
                (name, getattr(row, k) if getattr(row, k) is not None else u'')
                for (k, name) in self.csv_header
                ])

    def all(self):
        return list(self)
