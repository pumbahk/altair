# -*- coding: utf-8 -*-

import os
import logging
import tempfile
import pickle
from io import BytesIO
from datetime import date, datetime
from collections import OrderedDict

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import and_, or_

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart.api import get_cart_setting
from altair.app.ticketing.cart.helpers import format_number as _format_number
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer
from altair.app.ticketing.core.models import StockType, Stock, Product, ProductItem, Organization
from altair.app.ticketing.sej.models import SejRefundTicket, SejTicket
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
    u'order.refund_total_amount': u'払戻合計金額',
    u'order.refund_transaction_fee': u'払戻決済手数料',
    u'order.refund_delivery_fee': u'払戻配送手数料',
    u'order.refund_system_fee': u'払戻システム利用料',
    u'order.refund_special_fee': u'払戻特別手数料',
    u'order.note': u'メモ',
    u'order.special_fee_name': u'特別手数料名',
    u'order.approval_no': u'マルチ決済受領番号',
    u'order.card_brand': u'カードブランド',
    u'order.card_ahead_com_code': u'仕向け先企業コード',
    u'order.card_ahead_com_name': u'仕向け先企業名',
    u'order.issuing_start_at': u'発券開始日時',
    u'order.issuing_end_at': u'発券期限',
    u'order.payment_start_at': u'支払開始日時',
    u'order.payment_due_at': u'支払期限',
    u'order.cart_setting_id': u'カート設定',
    u'anshin_checkout.order_id': u'楽天ID決済 注文番号',
    u'anshin_checkout.order_control_id': u'楽天ID決済 注文管理番号',
    u'anshin_checkout.used_point': u'楽天ID決済 利用ポイント数',
    u'anshin_checkout.sales_at': u'楽天ID決済 売上日時',
    u'sej_order.pay_store_name': u'SEJ払込店舗',
    u'sej_order.ticketing_store_name': u'SEJ引換店舗',
    u'sej_order.billing_number': u'SEJ払込票番号',
    u'sej_order.exchange_number': u'SEJ引換票番号',
    u'famiport_order.payment_shop_name': u'FM支払店舗',
    u'famiport_order.payment_reserve_number': u'FM予約番号',
    u'famiport_order.ticketing_shop_name': u'FM発券店舗',
    u'famiport_order.ticketing_reserve_number': u'FM引換用予約番号',
    u'user_profile.last_name': u'姓',
    u'user_profile.first_name': u'名',
    u'user_profile.last_name_kana': u'姓(カナ)',
    u'user_profile.first_name_kana': u'名(カナ)',
    u'user_profile.nick_name': u'ニックネーム',
    u'user_profile.sex': u'性別',
    u'membership.name': u'会員種別名',
    u'membergroup.name': u'会員グループ名',
    u'user_credential.auth_identifier': u'会員種別ID',
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
    u'payment_method.name': u'決済方法',
    u'delivery_method.name': u'引取方法',
    u'event.title': u'イベント',
    u'performance.name': u'公演',
    u'performance.code': u'公演コード',
    u'performance.start_on': u'公演日',
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
    u'mail_magazine.mail_permission': u'メールマガジン受信可否',
    u'seat.name': u'座席名',
    u'stock_holder.name': u'枠名',
    }

def get_japanese_columns(request):
    return dict(japanese_columns)

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

class ZipRenderer(SimpleRenderer):
    def __call__(self, record, context):
        zip = dereference(record, self.key, True)
        zip = ('%s-%s' % (zip[0:3], zip[3:])) if zip else ''
        return [
            ((u'', self.name, u''), zip)
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
        except:
            logger.exception(u'error occured during sending CSV data')
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
        PlainTextRenderer(u'user_profile.sex'),
        PlainTextRenderer(u'membership.name'),
        PlainTextRenderer(u'membergroup.name'),
        PlainTextRenderer(u'user_credential.auth_identifier'),
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

    def __init__(self, request, export_type=EXPORT_TYPE_ORDER, organization_id=None, localized_columns={}, excel_csv=False, session=DBSession):
        self.request = request
        self.export_type = export_type
        column_renderers = None
        if export_type == self.EXPORT_TYPE_ORDER:
            column_renderers = self.per_order_columns
        elif export_type == self.EXPORT_TYPE_SEAT:
            column_renderers = self.per_seat_columns
        if column_renderers is None:
            raise ValueError('export_type')
        self.column_renderers = column_renderers
        self.enable_fancy = excel_csv
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.localized_columns = localized_columns
        self.session = session
        self.organization = session.query(Organization).filter_by(id=self.organization_id).one()
        self.marshaller_factory = PickleMarshallerFactory()

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id, self.session)
        return self._mailsubscription_cache

    def iter_records_for_order(self, order):
        user_credential = order.user.first_user_credential if order.user else None
        member = order.user.member if order.user and order.user.member else None
        common_record = {
            u'order': order,
            u'sej_order': order.sej_order if order.sej_order else None,
            u'user_profile': order.user.user_profile if order.user else None,
            u'membership': order.membership,
            u'membergroup': member.membergroup if member else None,
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
        query = self.session.query(Order).join(
                SejRefundTicket, and_(SejRefundTicket.order_no==Order.order_no, SejRefundTicket.deleted_at==None)
            ).join(
                SejTicket, and_(SejTicket.barcode_number==SejRefundTicket.ticket_barcode_number, SejTicket.deleted_at==None)
            ).join(
                ProductItem, and_(ProductItem.id==SejTicket.product_item_id, ProductItem.deleted_at==None)
            ).join(
                Product, and_(Product.id==ProductItem.product_id, Product.deleted_at==None)
            ).join(
                Stock, and_(Stock.id==ProductItem.stock_id, Stock.deleted_at==None)
            ).join(
                StockType, and_(StockType.id==Stock.stock_type_id, StockType.deleted_at==None)
            ).filter(
                Order.refund_id==self.refund.id
            ).with_entities(
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
            )
        for row in query:
            yield OrderedDict([
                (name, getattr(row, k) if getattr(row, k) is not None else u'')
                for (k, name) in self.csv_header
                ])

    def all(self):
        return list(self)
