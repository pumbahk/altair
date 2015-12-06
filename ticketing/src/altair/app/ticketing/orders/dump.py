# -*- coding: utf-8 -*-
_ = lambda x: unicode(x)

import json
import datetime
import itertools
from pyramid.decorator import reify
from zope.interface import (
    Interface,
    Attribute,
    implementer,
    )
import csv

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql as sa_sql
import sqlalchemy.sql.functions as sa_func

from altair.app.ticketing.core.models import(
    Organization,
    ShippingAddress,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    Event,
    Performance,
    SalesSegment,
    SalesSegmentGroup,
    Seat,
    )
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    UserCredential,
    Member,
    MemberGroup,
    Membership,
    )
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    )
from altair.app.ticketing.sej.models import (
    SejOrder,
    )
from altair.app.ticketing.mailmags.models import (
    MailSubscription,
    MailMagazine,
    MailSubscriptionStatus,
    )
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )


def _bench(word):
    pass
    # import sys, time
    # print >> sys.stderr, time.clock()
    # print >> sys.stderr, word,

int_or_blank = lambda value: '' if value is None else int(value)
value_or_blank = lambda value: '' if value is None else value

class Compiler(object):
    pass

class OrderOrderNoCompiler(Compiler):
    def __init__(self, *order_nos):
        self.order_nos = order_nos

    name = u'予約番号'
    get = staticmethod(lambda order, **kwds: order.order_no)

class OrderStatusCompiler(Compiler):
    name = u'予約番号'
    get = staticmethod(lambda order, **kwds: order.status)

class OrderPaymentStatusCompiler(Compiler):
    name = u'決済ステータス'
    get = staticmethod(lambda order, **kwds: order.payment_status)

class OrderCreatedAtCompiler(Compiler):
    name = u'予約日時'
    get = staticmethod(lambda order, **kwds: order.created_at)

class OrderPaidAtCompiler(Compiler):
    name = u'支払日時'
    get = staticmethod(lambda order, **kwds: order.paid_at)

class OrderDeliveredAtCompiler(Compiler):
    name = u'配送日時'
    get = staticmethod(lambda order, **kwds: order.delivered_at)

class OrderCanceledAtCompiler(Compiler):
    name = u'キャンセル日時'
    get = staticmethod(lambda order, **kwds: order.canceled_at)

class OrderTotalAmountCompiler(Compiler):
    name = u'合計金額'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.total_amount))

class OrderTransactionFeeCompiler(Compiler):
    name = u'決済手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.transaction_fee))

class OrderDeliveryFeeCompiler(Compiler):
    name = u'配送手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.delivery_fee))

class OrderSystemFeeCompiler(Compiler):
    name = u'システム利用料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.system_fee))

class OrderSpecialFeeCompiler(Compiler):
    name = u'特別手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.special_fee))

class OrderSpecialFeeCompiler(Compiler):
    name = u'特別手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.special_fee))

class OrderRefundTotalAmountCompiler(Compiler):
    name = u'払戻合計金額'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_total_amount))


class OrderRefundTotalAmountCompiler(Compiler):
    name = u'払戻合計金額'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_total_amount))


class OrderRefundTransactionFeeCompiler(Compiler):
    name = u'払戻決済手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_transaction_fee))


class OrderRefundDeliveryFeeCompiler(Compiler):
    name = u'払戻配送手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_delivery_fee))


class OrderRefundSystemFeeCompiler(Compiler):
    name = u'払戻システム利用料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_system_fee))


class OrderRefundSpecialFeeCompiler(Compiler):
    name = u'払戻特別手数料'
    get = staticmethod(lambda order, **kwds: int_or_blank(order.refund_special_fee))


class OrderNoteCompiler(Compiler):
    name = u'メモ'
    get = staticmethod(lambda order, **kwds: order.note)


class OrderSpecialFeeNameCompiler(Compiler):
    name = u'特別手数料名'
    get = staticmethod(lambda order, **kwds: order.special_fee_name)


class OrderCardBrandCompiler(Compiler):
    name = u'カードブランド'
    get = staticmethod(lambda order, **kwds: order.card_brand)


class SejOrderTicketingStartAtCompiler(Compiler):
    name = u'発券開始日時'
    get = staticmethod(lambda sej_order, **kwds: sej_order.ticketing_start_at if sej_order else '')


class SejOrderTicketingDueAtCompiler(Compiler):
    name = u'発券期限'
    get = staticmethod(lambda sej_order, **kwds: sej_order.ticketing_due_at if sej_order else '')


class SejOrderPayAtCompiler(Compiler):
    name = u'支払日時'
    get = staticmethod(lambda sej_order, **kwds: sej_order.pay_at if sej_order else '')

class SejOrderPaymentDueAtCompiler(Compiler):
    name = u'支払期限'
    get = staticmethod(lambda sej_order, **kwds: sej_order.payment_due_at if sej_order else '')

class SejOrderBillingNumberCompiler(Compiler):
    name = u'払込票番号'
    get = staticmethod(lambda sej_order, **kwds: sej_order.billing_number if sej_order else '')

class SejOrderExchangeNumberCompiler(Compiler):
    name = u'引換票番号'
    get = staticmethod(lambda sej_order, **kwds: sej_order.exchange_number if sej_order else '')

class ShippingAddressLastNameCompiler(Compiler):
    name = u'姓'
    get = staticmethod(lambda order, **kwds: order.shipping_address.last_name if order.shipping_address else '')

class ShippingAddressFirstNameCompiler(Compiler):
    name = u'名'
    get = staticmethod(lambda order, **kwds: order.shipping_address.first_name if order.shipping_address else '')

class ShippingAddressLastNameKANACompiler(Compiler):
    name = u'姓(カナ)'
    get = staticmethod(lambda order, **kwds: order.shipping_address.last_name_kana if order.shipping_address else '')

class ShippingAddressFirstNameKANACompiler(Compiler):
    name = u'名(カナ)'
    get = staticmethod(lambda order, **kwds: order.shipping_address.first_name_kana if order.shipping_address else '')

class ShippingAddressNickNameCompiler(Compiler):
    name = u'ニックネーム'
    get = staticmethod(lambda order, **kwds: order.shipping_address.nick_name if order.shipping_address else '')

class ShippingAddressSexCompiler(Compiler):
    name = u'性別'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.sex)

class UserProfileLastNameCompiler(Compiler):
    name = u'姓'
    get = staticmethod(lambda user_profile, **kwds: user_profile.last_name if user_profile else '')

class UserProfileFirstNameCompiler(Compiler):
    name = u'名'
    get = staticmethod(lambda user_profile, **kwds: user_profile.first_name if user_profile else '')

class UserProfileLastNameKANACompiler(Compiler):
    name = u'姓(カナ)'
    get = staticmethod(lambda user_profile, **kwds: user_profile.last_name_kana if user_profile else '')

class UserProfileFirstNameKANACompiler(Compiler):
    name = u'名(カナ)'
    get = staticmethod(lambda user_profile, **kwds: user_profile.first_name_kana if user_profile else '')

class UserProfileNickNameCompiler(Compiler):
    name = u'ニックネーム'
    get = staticmethod(lambda user_profile, **kwds: user_profile.nick_name if user_profile else '')

class UserProfileSexCompiler(Compiler):
    name = u'性別'
    get = staticmethod(lambda user_profile, **kwds: user_profile and user_profile.sex)

class MembershipNameCompiler(Compiler):
    name = u'会員区分名'
    get = staticmethod(lambda membership, **kwds: membership and membership.name)

class MemberGroupNameCompiler(Compiler):
    name = u'会員グループ名'
    get = staticmethod(lambda membergroup, **kwds: membergroup and membergroup.name)

class PaymentMethodNameCompiler(Compiler):
    name = u'決済方法名称'
    get = staticmethod(lambda payment_method, **kwds: payment_method.name)

class DeliveryMethodNameCompiler(Compiler):
    name = u'配送方法名称'
    get = staticmethod(lambda delivery_method, **kwds: delivery_method.name)

class ShippingAddressZipCompiler(Compiler):
    name = u'郵便番号'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.zip)

class ShippingAddressCountryCompiler(Compiler):
    name = u'国'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.country)

class ShippingAddressPrefectureCompiler(Compiler):
    name = u'都道府県'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.prefecture)

class ShippingAddressCityCompiler(Compiler):
    name = u'市区町村'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.city)

class ShippingAddressAddress1Compiler(Compiler):
    name = u'住所1'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.address_1)

class ShippingAddressAddress2Compiler(Compiler):
    name = u'住所2'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.address_2)

class ShippingAddressTel1Compiler(Compiler):
    name = u'電話番号1'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.tel_1)

class ShippingAddressTel2Compiler(Compiler):
    name = u'電話番号2'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.tel_2)

class ShippingAddressEmail1Compiler(Compiler):
    name = u'メールアドレス1'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.email_1)

class ShippingAddressEmail2Compiler(Compiler):
    name = u'メールアドレス2'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.email_2)

class ShippingAddressFaxCompiler(Compiler):
    name = u'FAX'
    get = staticmethod(lambda shipping_address, **kwds: shipping_address and shipping_address.fax)

class EventTitleCompiler(Compiler):
    name = u'イベント'
    get = staticmethod(lambda event, **kwds: event.title)

    def __init__(self, event_id):
        self.event_id = int(event_id)

    def filter(self, qs):
        if self.event_id:
            qs = qs.filter(Event.id==self.event_id)
        return qs

class SalesSegmentGroupNameCompiler(Compiler):
    name = u'販売区分'
    get = staticmethod(lambda performance, **kwds: performance.name)

class PerformanceNameCompiler(Compiler):
    name = u'公演'
    get = staticmethod(lambda performance, **kwds: performance.name)

    def __init__(self, *ids):
        self.ids = ids

    def filter(self, qs):
        if self.ids:
            qs = qs.filter(Performance.id.in_(self.ids))
        return qs

class PerformanceCodeCompiler(Compiler):
    name = u'公演コード'
    get = staticmethod(lambda performance, **kwds: performance.code)

class PerformanceStartOnCompiler(Compiler):
    name = u'公演日'
    get = staticmethod(lambda performance, **kwds: performance.start_on)

class VenueNameCompiler(Compiler):
    name = u'会場名'
    get = staticmethod(lambda venue, **kwds: venue.name)

class OrderProductCountCompiler(Compiler):
    name = u'枚数'

    @staticmethod
    def get(order, **kwds):
        return sum(ordered_product_item.quantity
                   for ordered_product in order.ordered_products
                   for ordered_product_item in ordered_product.ordered_product_items
                   )

class UserCredentialAuthIdentiferCompiler(Compiler):
    name = u'会員種別ID'
    get = staticmethod(lambda user_credential, **kwds: user_credential and user_credential[0].auth_identifier)

class MarginCompiler(Compiler):
    name = u'内手数料金額'

    @staticmethod
    def get(order, **kwds):
        margin = order.sales_segment.margin_ratio / 100
        return sum(ordered_product.price * ordered_product.quantity for ordered_product in order.ordered_products) * margin

class OrderCardAHeadComCodeCompiler(Compiler):
    name = u'仕向け先企業コード'
    get = staticmethod(lambda order, **kwds: order.card_ahead_com_code)

class OrderCardAHeadComNameCompiler(Compiler):
    name = u'仕向け先企業名'
    get = staticmethod(lambda order, **kwds: order.card_ahead_com_name)

class MailMagazinePermissionCompiler(Compiler):
    name = u'メールマガジン受信可否'
    get = staticmethod(lambda shipping_address, subscribed_emails, **kwds: bool(shipping_address and ((shipping_address.email_1 in subscribed_emails) or (shipping_address.email_2 or shipping_address.email_2 in subscribed_emails))))

class LotNameCompiler(Compiler):
    name = u'抽選'

    @staticmethod
    def get(order, lotentries, **kwds):
        lotentry = lotentries.get(order.order_no, None)
        return lotentry.lot.name if lotentry else None

class Context(object):
    pass

class OrderExportContext(Context):
    def __init__(self, order, sej_orders, subscribed_emails, lotentries):
        self.order = order
        self.shipping_address = order.shipping_address
        self.performance = order.performance
        self.event = order.performance.event
        self.venue = order.performance.venue
        self.pdmp = order.payment_delivery_pair
        self.payment_method = order.payment_delivery_pair.payment_method
        self.delivery_method = order.payment_delivery_pair.delivery_method

        self.user = order.user
        self.user_credential = None
        self.user_profile = None
        self.membergroup = order.membergroup
        self.membership = order.membership

        if self.user:
            self.user_credential = self.user.user_credential
            self.user_profile = self.user.user_profile

        self._sej_orders = sej_orders
        self._subscribed_emails = subscribed_emails
        self._lotentries = lotentries

class OrderExportAdapter(object):
    def __init__(self, order, sej_orders, subscribed_emails, lotentries):
        self._order = order
        self._performance = self._order.performance
        self._event = self._performance.event
        self._venue = self._performance.venue
        self._pdmp = self._order.payment_delivery_pair
        self._payment_method = self._pdmp.payment_method
        self._delivery_method = self._pdmp.delivery_method
        self._sej_orders = sej_orders
        self._subscribed_emails = subscribed_emails
        self._lotentries = lotentries

        self._shipping_address = order.shipping_address
        self._user = order.user

        self._user_credential = None
        self._user_profile = None
        self._membergroup = self._order.membergroup
        self._membership = self._order.membership

        if self._user:
            self._user_credential = self._user.user_credential
            self._user_profile = self._user.user_profile

    def get(self, compiler):
        return compiler.get(
            order=self._order,
            payment_method=self._payment_method,
            delivery_method=self._delivery_method,
            shipping_address=self._shipping_address,
            sej_order=self.sej_order,
            user=self._user,
            membergroup=self._membergroup,
            membership=self._membership,
            performance=self._performance,
            event=self._event,
            venue=self._venue,
            user_credential=self._user_credential,
            user_profile=self._user_profile,
            subscribed_emails=self._subscribed_emails,
            lotentries=self._lotentries,
            )

    @reify
    def sej_order(self):
        return self._sej_orders.get(self._order.order_no, None)


column_compiler = {
    "order-no": OrderOrderNoCompiler,
    "ORDER_STATUS": OrderStatusCompiler,
    "ORDER_PAYMENT_STATUS": OrderPaymentStatusCompiler,
    "ORDER_CREATED_AT": OrderCreatedAtCompiler,
    "ORDER_PAID_AT": OrderPaidAtCompiler,
    "ORDER_DELIVERED_AT": OrderDeliveredAtCompiler,
    "ORDER_CANCELED_AT": OrderCanceledAtCompiler,
    "LOT_NAME": LotNameCompiler,
    "ORDER_TOTAL_AMOUNT": OrderTotalAmountCompiler,
    "ORDER_TRANSACTION_FEE": OrderTransactionFeeCompiler,
    "ORDER_DELIVERY_FEE": OrderDeliveryFeeCompiler,
    "ORDER_SYSTEM_FEE": OrderSystemFeeCompiler,
    "ORDER_SPECIAL_FEE": OrderSpecialFeeCompiler,
    "MARGIN": MarginCompiler,
    "ORDER_REFUD_TOTAL_AMOUNT": OrderRefundTotalAmountCompiler,
    "ORDER_REFUND_TRANSACTION_FEE": OrderRefundTransactionFeeCompiler,
    "ORDER_REFUND_DELIVERY_FEE": OrderRefundDeliveryFeeCompiler,
    "ORDER_REFUND_SYSTEM_FEE": OrderRefundSystemFeeCompiler,
    "ORDER_REFUND_SPECIAL_FEE": OrderRefundSpecialFeeCompiler,
    "ORDER_NOTE": OrderNoteCompiler,
    "ORDER_SPECIAL_FEE_NAME": OrderSpecialFeeNameCompiler,
    "ORDER_CARD_BRAND": OrderCardBrandCompiler,
    "ORDER_CARD_AHEAD_COM_CODE": OrderCardAHeadComCodeCompiler,
    "ORDER_CARD_AHEAD_COM_NAME": OrderCardAHeadComNameCompiler,
    "SEJORDER_TICKETING_START_AT": SejOrderTicketingStartAtCompiler,
    "SEJORDER_TICKETING_DUE_AT": SejOrderTicketingDueAtCompiler,
    "SEJORDER_PAY_AT": SejOrderPayAtCompiler,
    "SEJORDER_PAYMENT_DUE_AT": SejOrderPaymentDueAtCompiler,
    "SEJORDER_BILLING_NUMBER": SejOrderBillingNumberCompiler,
    "SEJORDER_EXCHANGE_NUMBER": SejOrderExchangeNumberCompiler,
    "MAIL_MAGAZINE_PERMISSION": MailMagazinePermissionCompiler,
    "USERPROFILE_LAST_NAME": UserProfileLastNameCompiler,
    "USERPROFILE_FIRST_NAME": UserProfileFirstNameCompiler,
    "USERPROFILE_LAST_NAME_KANA": UserProfileLastNameKANACompiler,
    "USERPROFILE_FIRST_NAME_KANA": UserProfileFirstNameKANACompiler,
    "USERPROFILE_NICK_NAME": UserProfileNickNameCompiler,
    "USERPROFILE_SEX": UserProfileSexCompiler,
    "MEMBER_SHIP_NAME": MembershipNameCompiler,
    "MEMBER_GROUP_NAME": MemberGroupNameCompiler,
    "USER_CREDENTIAL_AUTH_IDENTIFIER": UserCredentialAuthIdentiferCompiler,
    "SHIPPINGADDRESS_LAST_NAME": ShippingAddressLastNameCompiler,
    "SHIPPINGADDRESS_FIRST_NAME": ShippingAddressFirstNameCompiler,
    "SHIPPINGADDRESS_LAST_NAME_KANA": ShippingAddressLastNameKANACompiler,
    "SHIPPINGADDRESS_FIRST_NAME_KANA": ShippingAddressFirstNameKANACompiler,
    "SHIPPINGADDRESS_ZIP": ShippingAddressZipCompiler,
    "SHIPPINGADDRESS_COUNTRY": ShippingAddressCountryCompiler,
    "SHIPPINGADDRESS_PREFECTURE": ShippingAddressPrefectureCompiler,
    "SHIPPINGADDRESS_CITY": ShippingAddressCityCompiler,
    "SHIPPINGADDRESS_ADDRESS_1": ShippingAddressAddress1Compiler,
    "SHIPPINGADDRESS_ADDRESS_2": ShippingAddressAddress2Compiler,
    "SHIPPINGADDRESS_TEL_1": ShippingAddressTel1Compiler,
    "SHIPPINGADDRESS_TEL_2": ShippingAddressTel2Compiler,
    "SHIPPINGADDRESS_FAX": ShippingAddressFaxCompiler,
    "SHIPPINGADDRESS_EMAIL_1": ShippingAddressEmail1Compiler,
    "SHIPPINGADDRESS_EMAIL_2": ShippingAddressEmail2Compiler,
    "PAYMENTMETHOD_NAME": PaymentMethodNameCompiler,
    "DELIVERYMETHOD_NAME": DeliveryMethodNameCompiler,
    "event": EventTitleCompiler,
    "SALESSEGMENTGROUP_NAME": SalesSegmentGroupNameCompiler,
    "performance": PerformanceNameCompiler,
    "PERFORMANCE_CODE": PerformanceCodeCompiler,
    "PERFORMANCE_START_ON": PerformanceStartOnCompiler,
    "VENUE_NAME": VenueNameCompiler,
    "ORDER_PRODUCT_COUNT": OrderProductCountCompiler,
    #"SEAT_NO": None,
    }



from wtforms.form import Form
from wtforms.fields import StringField
from wtforms.widgets import TextInput


class FilterBuildError(Exception):
    pass


class QBuilder(object):
    name = u'-'
    _type = None
    _targets = None

    def __init__(self, *values):
        self._values = map(self._type, values)

    def filter(self, qs):
        return qs

    def after_filter(self):
        pass


class QBuilderIn(QBuilder):
    def filter(self, qs):
        if self._values and self._targets:
            qs = qs.filter(sa.or_(*[target.in_(self._values) for target in self._targets]))
        return qs


class QBuilderBetween(QBuilder):
    def filter(self, qs):
        if self._values and self._targets:
            qs = qs.filter(sa.or_(*[target.between(*self._values) for target in self._targets]))
        return qs


class QBuilderSearch(QBuilder):
    def filter(self, qs):
        if self._values:
            for value in self._values and self._targets:
                pattern = '%{}%'.format(value)
                qs = qs.filter(sa.or_(*[target.like(pattern) for target in self._targets]))
        return qs


# class InFilter(BaseFilter):
#     def filter(self, qs):
#         if self._values:
#             qs = qs.filter(self._target.in_(self._values))
#         return qs

# class SearchFilter(BaseFilter):
#     def __init__(self, *values):
#         self._values = []
#         super(self).__init__(*values)
#         if len(self._values) > 1:
#             raise FilterBuildError()
#         self._value = self._values[0]

#     def filter(self, qs):
#         if self._value:
#             qs = qs.filter(
#                 self._target.like('%{}%'.format(self._value)))
#         return qs


# class EqualFilter(BaseFilter):
#     def __init__(self, *values):
#         self._values = []
#         super(self).__init__(*values)
#         if len(self._values) > 1:
#             raise FilterBuildError()
#         self._value = self._values[0]

#     def filter(self, qs):
#         if self._value:
#             qs = qs.filter(self._target==self._value)
#         return qs

class OrderNoQBuilder(QBuilderIn):
    name = u'予約番号'
    _type = unicode
    _targets = Order.order_no,

class SeatNoQBuilder(QBuilderSearch):
    name = u'座席番号'
    _type = unicode
    _targets = Seat.seat_no,

class NameQBuilder(QBuilderSearch):
    name = u'名前'
    _type = unicode
    _targets = (
        ShippingAddress.last_name,
        ShippingAddress.first_name,
        ShippingAddress.last_name_kana,
        ShippingAddress.first_name_kana,
        UserProfile.last_name,
        UserProfile.first_name,
        UserProfile.last_name_kana,
        UserProfile.first_name_kana,
        UserProfile.nick_name,
        )

class EventQBuilder(QBuilderIn):
    name = u'イベント'
    _type = int
    _targets = Event.id,

class PerformanceQBuilder(QBuilderIn):
    name = u'パフォーマンス'
    _type = int
    _targets = Performance.id,

class SalesSegmentGroupQBuilder(QBuilderIn):
    name = u'販売区分'
    _type = int
    _targets = SalesSegmentGroup.id,

class TelephoneQBuilder(QBuilderIn):
    name = u'電話番号'
    _type = lambda tel_number: unicode(tel_number).replace('-', '').strip()
    _targets = (
        ShippingAddress.tel_1,
        ShippingAddress.tel_2,
        UserProfile.tel_1,
        UserProfile.tel_2,
        )


class EmailQBuilder(QBuilderIn):
    name = u'メールアドレス'
    _type = unicode
    _targets = (
        ShippingAddress.email_1,
        ShippingAddress.email_2,
        UserProfile.email_1,
        UserProfile.email_2,
        )

class MemberQBuilder(QBuilderIn):
    name = u'会員番号'
    _type = unicode
    _targets = UserCredential.auth_identifier,

class OrderStatusQBuilder(QBuilderIn):
    name = u'予約ステータス'
    _type = unicode
    _targets = ()

class PaymentStatusQBuilder(QBuilderIn):
    name = u'決済ステータス'
    _type = unicode
    _targets = ()

class PrintStatusQBuilder(QBuilderIn):
    name = u'発券ステータス'
    _type = unicode
    _targets = ()

class CountQBuilder(QBuilderIn):
    name = u'購入枚数'
    _type = unicode
    _targets = ()

class PaymentMethodQBuilder(QBuilderIn):
    name = u'決済方法'
    _type = int
    _targets = PaymentMethod.id,

class DeliveryMethodQBuilder(QBuilderIn):
    name = u'引取方法'
    _type = int
    _targets = DeliveryMethod.id

class OrderedAtQBuilder(QBuilderBetween):
    name = u'予約日時'
    _type = datetime.datetime
    _targets = Order.created_at,

    def __init__(self, *values):
        def _convert(datestr):
            fmts = ['%Y-%m-%dT%H:%M:%S']
            for fmt in fmts:
                try:
                    return datetime.datetime.strptime(datestr, fmt)
                except ValueError as err: # does not match format
                    continue
            raise ValueError('time date "{}" does not match formats'.format(datestr))
        self._values = map(_convert, values)


class PerformanceStartOnQBuilder(QBuilderBetween):
    name = u'公演開始日時'
    _type = dict
    _targets = Performance.start_on,


name_filter = {
    'order-no': OrderNoQBuilder,
    'seat-no': SeatNoQBuilder,
    'name': NameQBuilder,
    'event': EventQBuilder,
    'performance': PerformanceQBuilder,
    'salessegmentgroup': SalesSegmentGroupQBuilder,
    'telephone': TelephoneQBuilder,
    'email': EmailQBuilder,
    'member': MemberQBuilder,
    'order-status': OrderStatusQBuilder,
    'payment-status': PaymentStatusQBuilder,
    'print-status': PrintStatusQBuilder,
    'count': CountQBuilder,
    'payment-method': PaymentMethodQBuilder,
    'delivery-method': DeliveryMethodQBuilder,
    'ordered-at': OrderedAtQBuilder,
    'performance-start-on': PerformanceStartOnQBuilder,
    }


class FilterFactory(object):
    def create(self, name, params):
        try:
            klass = name_filter[name]
            return klass(*params)
        except KeyError:
            raise

    def creates(self, paramses):
        return [self.create(name, params) for name, params in paramses.items()]


import bisect
class SpeedySearcher(object):
    def __init__(self, elms):
        self._elms = sorted(elms)

    def __len__(self):
        return len(self._elms)

    def __getitem__(self, index):
        return self._elms[index]

    def __contains__(self, target):
        index = bisect.bisect_left(self._elms, target)
        return index < len(self) and self[index] == target


class OrderExporter(object):
    def __init__(self, session, organization_id=None):
        self._session = session
        self.organization_id = organization_id

    def _build_query(self, filters):
        qs = self._session.query(Order) \
          .join(Order.sales_segment) \
          .join(SalesSegment.sales_segment_group)\
          .join(SalesSegmentGroup.event) \
          .outerjoin(Order.shipping_address)\
          .outerjoin(Order.payment_delivery_pair)\
          .outerjoin(PaymentDeliveryMethodPair.payment_method)\
          .outerjoin(PaymentDeliveryMethodPair.delivery_method)\
          .outerjoin(Order.items)\
          .outerjoin(OrderedProduct.elements)\
          .outerjoin(Order.user)\
          .outerjoin(User.user_credential)\
          .outerjoin(Order.membergroup)\
          .outerjoin(Order.membership)\
          .options(
            sa_orm.contains_eager('sales_segment'),
            sa_orm.contains_eager('shipping_address'),
            sa_orm.contains_eager('items'),
            sa_orm.contains_eager('membergroup'),
            sa_orm.contains_eager('membership'),
            sa_orm.contains_eager('items', 'elements'),
            sa_orm.contains_eager('payment_delivery_pair'),
            sa_orm.contains_eager('payment_delivery_pair', 'payment_method'),
            sa_orm.contains_eager('payment_delivery_pair', 'delivery_method'))


        # order_noが重複しているモノを消し去る こんなコード入れたら遅いかな...
        order_one = sa_orm.aliased(Order)
        subqs = sa.select([sa_func.max(order_one.branch_no)])\
          .where(order_one.order_no==Order.order_no)
        qs = qs.filter(Order.branch_no==subqs)

        if self.organization_id:
            qs = qs.filter(Order.organization_id==self.organization_id)

        filter_factory = FilterFactory()
        filters = filter_factory.creates(filters)
        for filter_ in filters:
            qs = filter_.filter(qs)
        qs = qs.order_by(sa.desc(Order.id))
        return qs

    def get_order_no_sej_order(self, order_nos):
        sej_orders = self._session\
          .query(SejOrder)\
          .filter(SejOrder.order_no.in_(order_nos))\
          .all()
        order_no_sej_order = dict((sej_order.order_no, sej_order)
                                  for sej_order in sej_orders)
        return order_no_sej_order

    def get_subscribed_emails(self, organization_id=None, targets=[]):
        qs = self._session\
            .query(MailSubscription)\
            .filter(sa.or_(MailSubscription.status==None, MailSubscription.status==MailSubscriptionStatus.Subscribed.v))
        if organization_id:
            qs = qs.filter(MailMagazine.organization_id==organization_id)
        if targets:
            qs = qs.filter(MailSubscription.email.in_(targets))
        qs = qs.with_entities(MailSubscription.email)
        return qs.all()

    def get_order_no_lot_entry(self, order_nos):
        lot_entries = self._session\
          .query(LotEntry)\
          .filter(LotEntry.entry_no.in_(order_nos))\
          .all()
        return dict((lot_entry.entry_no, lot_entry)
                    for lot_entry in lot_entries)

    def create_adapters(self, orders, order_no_sej_order, subscribed_emails, order_no_lot_entry):
        return [OrderExportAdapter(order, order_no_sej_order, subscribed_emails, order_no_lot_entry)
                for order in orders]

    def create_contexts(self, orders, order_no_sej_order, subscribed_emails, order_no_lot_entry):
        return [OrderExportContext(order, order_no_sej_order, subscribed_emails, order_no_lot_entry)
                for order in orders]

    def create_rows(self, adapters, compilers):
        return [
            [unicode(value_or_blank(adapter.get(compiler))).encode('cp932') for compiler in compilers]
            for adapter in adapters
            ]

    def exportfp(self, fp, options=[], filters={}, limit=None, json_=None):
        if json_:
            data = json.loads(json_)
            filters = data['filters']
            options = data['options']
            limit = data['limit']


        qs = self._build_query(filters)
        if limit is not None:
            qs = qs.limit(limit + int(limit * 0.5))
        orders = qs.all()
        orders = orders[:limit]
        _bench('ORDER LENGTH: {}'.format(len(orders)))
        order_nos = (order.order_no for order in orders)
        emai1_email2 = ((order.shipping_address.email_1, order.shipping_address.email_2)
                         for order in orders
                         if order.shipping_address
                         )
        _email_chain = itertools.chain(*emai1_email2)
        emails = set(email for email in _email_chain if email)

        _bench('SEJ Order')
        order_no_sej_order = self.get_order_no_sej_order(order_nos)

        _bench('Mail permission')
        subscribed_emails = self.get_subscribed_emails(self.organization_id, emails)
        subscribed_emails = SpeedySearcher(subscribed_emails)

        _bench('Lots')
        order_no_lot_entry = self.get_order_no_lot_entry(order_nos)

        _bench('Adapters')
        # contexts = self.create_contexts(orders, order_no_sej_order, subscribed_emails, order_no_lot_entry)
        # for filter_ in filters:
        #     contexts = filter_.after_filter(contexts)
        adapters = self.create_adapters(orders, order_no_sej_order, subscribed_emails, order_no_lot_entry)

        _bench('Compiler')
        compilers = [column_compiler[option] for option in options]
        header = [compiler.name.encode('cp932') for compiler in compilers]

        _bench('create rows')
        rows = self.create_rows(adapters, compilers)
        _bench('FINISH')
        writer = csv.writer(fp)
        writer.writerow(header)
        writer.writerows(rows)

    def export(self, path, *args, **kwds):
        with open(path, 'w+b') as fp:
            self.exportfp(fp, *args, **kwds)
