# -*- coding: utf-8 -*-

from collections import OrderedDict

from paste.util.multidict import MultiDict
from sqlalchemy.sql.expression import or_

from altair.app.ticketing.cart.helpers import format_number as _format_number
from altair.app.ticketing.mailmags.models import MailSubscription, MailMagazine, MailSubscriptionStatus
from altair.app.ticketing.utils import dereference
from altair.app.ticketing.csvutils import CSVRenderer, PlainTextRenderer, CollectionRenderer, AttributeRenderer, SimpleRenderer
from .api import get_ordered_product_metadata_provider_registry

def format_number(value):
    return _format_number(float(value))

def _create_mailsubscription_cache(organization_id):
    D = dict()
    query = MailSubscription.query\
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
    u'order.total_amount': u'合計金額',
    u'order.transaction_fee': u'決済手数料',
    u'order.delivery_fee': u'配送手数料',
    u'order.system_fee': u'システム利用料',
    u'order.special_fee': u'特別手数料',
    u'order.margin': u'内手数料金額',
    u'order.note': u'メモ',
    u'order.special_fee_name': u'特別手数料名',
    u'order.card_brand': u'カードブランド',
    u'order.card_ahead_com_code': u'仕向け先企業コード',
    u'order.card_ahead_com_name': u'仕向け先企業名',
    u'sej_order.billing_number': u'SEJ払込票番号',
    u'sej_order.exchange_number': u'SEJ引換票番号',
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
    u'ordered_product.product.name': u'商品名',
    u'ordered_product.product.sales_segment.sales_segment_group.name': u'販売区分',
    u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
    u'ordered_product_item.product_item.name': u'商品明細名',
    u'ordered_product_item.price': u'商品明細単価',
    u'ordered_product_item.quantity': u'商品明細個数',
    u'ordered_product_item.print_histories': u'発券作業者',
    u'mail_magazine.mail_permission': u'メールマガジン受信可否',
    u'seat.name': u'座席名',
    }

def get_japanese_columns(request):
    retval = dict(japanese_columns)
    registry = get_ordered_product_metadata_provider_registry(request)
    for provider in registry.getProviders():
        for key in provider:
            metadata = provider[key]
            retval[u'attribute[%s]' % metadata.key] = metadata.get_display_name('ja_JP')
    return retval

class MarginRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
        order = dereference(record, self.key)
        rendered_value = 0
        for ordered_product in order.ordered_products:
            margin = (ordered_product.product.sales_segment.margin_ratio / 100) if ordered_product.product.sales_segment is not None else 0
            rendered_value += (ordered_product.price * ordered_product.quantity) * margin
        return [
            ((u"", self.column_name, u""), unicode(rendered_value))
        ]

class PerSeatQuantityRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
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
        self.outer = None

    def __call__(self, record):
        assert self.outer is not None
        emails = dereference(record, self.key, True) or []
        return [
            (
                (u"", self.column_name, u""),
                one_or_empty(any(self.outer.mailsubscription_cache.get(email, False) for email in emails))
                )
            ]

class CurrencyRenderer(SimpleRenderer):
    def __call__(self, record):
        return [
            ((u'', self.name, u''), unicode(format_number(dereference(record, self.key))))
            ]

class ZipRenderer(SimpleRenderer):
    def __call__(self, record):
        zip = dereference(record, self.key, True)
        zip = ('%s-%s' % (zip[0:3], zip[3:])) if zip else ''
        return [
            ((u'', self.name, u''), zip)
        ]

class PrintHistoryRenderer(object):
    def __init__(self, key, column_name):
        self.key = key
        self.column_name = column_name

    def __call__(self, record):
        ordered_product_item = dereference(record, self.key)
        return [
            (
                (u"", self.column_name, u""),
                u", ".join(list(OrderedDict([(print_history.operator.name, True) for print_history in ordered_product_item.print_histories if print_history.operator is not None])))
                )
            ]

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
        CurrencyRenderer(u'order.total_amount'),
        CurrencyRenderer(u'order.transaction_fee'),
        CurrencyRenderer(u'order.delivery_fee'),
        CurrencyRenderer(u'order.system_fee'),
        CurrencyRenderer(u'order.special_fee'),
        MarginRenderer(u'order', u'order.margin'),
        PlainTextRenderer(u'order.note'),
        PlainTextRenderer(u'order.special_fee_name'),
        PlainTextRenderer(u'order.card_brand'),
        PlainTextRenderer(u'order.card_ahead_com_code'),
        PlainTextRenderer(u'order.card_ahead_com_name'),
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
            ]

    per_seat_columns = \
        common_columns_pre + \
        [
            CurrencyRenderer(u'ordered_product.price'),
            PlainTextRenderer(u'ordered_product.quantity'),
            PlainTextRenderer(u'ordered_product.product.name'),
            PlainTextRenderer(u'ordered_product.product.sales_segment.sales_segment_group.name'),
            PlainTextRenderer(u'ordered_product_item.product_item.name'),
            CurrencyRenderer(u'ordered_product_item.price'),
            PerSeatQuantityRenderer(u'ordered_product_item', u'ordered_product_item.quantity'),
            PrintHistoryRenderer(u'ordered_product_item', u'ordered_product_item.print_histories'),
            PlainTextRenderer(u'seat.name'),
            AttributeRenderer(
                u'ordered_product_item.attributes',
                u'attribute'
                ),
            ]

    def __init__(self, export_type=EXPORT_TYPE_ORDER, organization_id=None, localized_columns={}, excel_csv=False):
        self.export_type = export_type
        column_renderers = None
        if export_type == self.EXPORT_TYPE_ORDER:
            column_renderers = self.per_order_columns
        elif export_type == self.EXPORT_TYPE_SEAT:
            column_renderers = self.per_seat_columns
        if column_renderers is None:
            raise ValueError('export_type')

        def bind(column_renderer):
            if isinstance(column_renderer, MailMagazineSubscriptionStateRenderer):
                column_renderer = MailMagazineSubscriptionStateRenderer(column_renderer.key, column_renderer.column_name)
                column_renderer.outer = self
            elif isinstance(column_renderer, PlainTextRenderer) and column_renderer.fancy and not excel_csv:
                column_renderer = PlainTextRenderer(
                    column_renderer.key,
                    column_renderer.name,
                    column_renderer.empty_if_dereference_fails
                    )
            return column_renderer

        self.column_renderers = map(bind, column_renderers)
        self.organization_id = organization_id
        self._mailsubscription_cache = None
        self.localized_columns = localized_columns

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id)
        return self._mailsubscription_cache

    def iter_records(self, order):
        user_credential = order.user.first_user_credential if order.user else None
        member = order.user.member if order.user and order.user.member else None
        common_record = {
            u'order': order,
            u'sej_order': order.sej_order if order.sej_order else None,
            u'user_profile': order.user.user_profile if order.user else None,
            u'membership': user_credential.membership if user_credential else None,
            u'membergroup': member.membergroup if member else None,
            u'user_credential': user_credential,
            u'shipping_address': order.shipping_address,
            u'payment_method': order.payment_delivery_pair.payment_method,
            u'delivery_method': order.payment_delivery_pair.delivery_method,
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

    def __call__(self, orders):
        renderer = CSVRenderer(self.column_renderers)
        for order in orders:
            for record in self.iter_records(order):
                renderer.append(record)
        return renderer(localized_columns=self.localized_columns)
