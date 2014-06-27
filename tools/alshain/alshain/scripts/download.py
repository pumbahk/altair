# -*- coding: utf-8 -*-
import sys
import time
import argparse
import datetime
import StringIO as io

import sqlalchemy
from sqlalchemy import (
    or_,
    )
import pyramid.request
import pyramid.paster
import pyramid.testing
import transaction
import mako.template
import altair.sqlahelper

from altair.app.ticketing.core.models import(
    Organization,
    ShippingAddress,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    )
from altair.app.ticketing.users.models import (
    User,
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
    import sys, time
    print >> sys.stderr, time.clock()
    print >> sys.stderr, word,

DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'

class Compiler(object):
    name = str()
    entity = None
    type_ = staticmethod(lambda val: val)
    is_range = False  # boolean
    joins = []

    @classmethod
    def validate(cls, *args):
        if cls.is_range:
            first = None
            last = None
            try:
                first = args[0]
                last = args[1]
            except IndexError:
                pass  # ignore
            if first is not None:
                first = cls.type_(first)
            if last is not None:
                last = cls.type_(last)
            return first, last
        else:
            return map(cls.type_, args)

    @classmethod
    def compile(cls, qs, *args):
        qs = cls.join(qs)
        if cls.is_range:
            from_, to_ = cls.validate(*args)
            if from_:
                print 'FROM:', from_
                qs = qs.filter(cls.entity>=from_)
            if to_:
                qs = qs.filter(cls.entity<=to_)
        else:
            values = cls.validate(*args)
            if values:
                qs = qs.filter(cls.entity.in_(values))
        return qs

    @classmethod
    def join(cls, qs):
        for klass in cls.joins:
            qs = qs.join(klass)
        return qs


class OrderIndexCompiler(Compiler):
    name = u'予約ID'
    entity = Order.id
    type_ = int

class OrderOrderNoCompiler(Compiler):
    name = u'予約番号'
    entity = Order.id
    type_ = str

class OrderBranchNoCompiler(Compiler):
    name = u'ブランチ番号'
    entity = Order.id
    type_ = int

coerce_datetime = lambda val: datetime.datetime.strptime(val, DATETIME_FORMAT)

class OrderDeliveredAtCompiler(Compiler):
    name = u'配送日時'
    entity = Order.delivered_at
    is_range = True
    type_ = staticmethod(coerce_datetime)


class OrderPaidAtCompiler(Compiler):
    name = u'決済日時'
    entity = Order.paid_at
    is_range = True
    type_ = staticmethod(coerce_datetime)


class OrderCanceledAtCompiler(Compiler):
    name = u'キャンセル日時'
    entity = Order.canceled_at
    is_range = True
    type_ = staticmethod(coerce_datetime)


class OrderCreatedAtCompiler(Compiler):
    name = u'予約日時'
    entity = Order.created_at
    is_range = True
    type_ = staticmethod(coerce_datetime)


class OrderRefundedAtCompiler(Compiler):
    name = u'払戻日時'
    entity = Order.refunded_at
    is_range = True
    type_ = staticmethod(coerce_datetime)


class ShippingAddressCreatedAtCompiler(Compiler):
    name = u'購入者作成日'
    entity = ShippingAddress.created_at
    is_range = True
    type_ = staticmethod(coerce_datetime)
    joins = [ShippingAddress]


class OrderedProductPriceCompiler(Compiler):
    name = u'商品単価'
    entity = OrderedProduct.price
    type_ = int
    is_range = True
    joins = [OrderedProduct]


class OrderOrderNoCompiler(Compiler):
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

class OrderCreatedAtCompiler(Compiler):
    name = u'予約日時'
    get = staticmethod(lambda order, **kwds: order.created_at)

class OrderDeliveredAtCompiler(Compiler):
    name = u'配送日時'
    get = staticmethod(lambda order, **kwds: order.delivered_at)

class OrderCanceledAtCompiler(Compiler):
    name = u'キャンセル日時'
    get = staticmethod(lambda order, **kwds: order.canceled_at)

class OrderTotalAmountCompiler(Compiler):
    name = u'合計金額'
    get = staticmethod(lambda order, **kwds: order.total_amount)

class OrderTransactionFeeCompiler(Compiler):
    name = u'決済手数料'
    get = staticmethod(lambda order, **kwds: order.transaction_fee)

class OrderDeliveryFeeCompiler(Compiler):
    name = u'配送手数料'
    get = staticmethod(lambda order, **kwds: order.delivery_fee)

class OrderSystemFeeCompiler(Compiler):
    name = u'システム利用料'
    get = staticmethod(lambda order, **kwds: order.system_fee)

class OrderSpecialFeeCompiler(Compiler):
    name = u'特別手数料'
    get = staticmethod(lambda order, **kwds: order.special_fee)

class OrderSpecialFeeCompiler(Compiler):
    name = u'特別手数料'
    get = staticmethod(lambda order, **kwds: order.special_fee)

class OrderRefundTotalAmountCompiler(Compiler):
    name = u'払戻合計金額'
    get = staticmethod(lambda order, **kwds: order.refund_total_amount)

class OrderRefundTotalAmountCompiler(Compiler):
    name = u'払戻合計金額'
    get = staticmethod(lambda order, **kwds: order.refund_total_amount)

class OrderRefundTransactionFeeCompiler(Compiler):
    name = u'払戻決済手数料'
    get = staticmethod(lambda order, **kwds: order.refund_transaction_fee)

class OrderRefundDeliveryFeeCompiler(Compiler):
    name = u'払戻配送手数料'
    get = staticmethod(lambda order, **kwds: order.refund_delivery_fee)

class OrderRefundSystemFeeCompiler(Compiler):
    name = u'払戻システム利用料'
    get = staticmethod(lambda order, **kwds: order.refund_system_fee)

class OrderRefundSpecialFeeCompiler(Compiler):
    name = u'払戻特別手数料'
    get = staticmethod(lambda order, **kwds: order.refund_special_fee)

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

class PerformanceNameCompiler(Compiler):
    name = u'公演'
    get = staticmethod(lambda performance, **kwds: performance.name)

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
    get = staticmethod(lambda shipping_address, subscribed_emails, **kwds: shipping_address and (shipping_address.email_1 in subscribed_emails or shipping_address.email_2 in subscribed_emails))

class LotNameCompiler(Compiler):
    name = u'抽選'

    @staticmethod
    def get(order, lotentries, **kwds):
        lotentry = lotentries.get(order.order_no, None)
        if lotentry:
            return lotentry.lot.name
        else:
            return None

from pyramid.decorator import reify
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
        self._member = None
        self._membergroup = None
        self._membership = None

        if self._user:
            self._user_credential = self._user.user_credential
            self._user_profile = self._user.user_profile
            self._member = self._user.member
            self._membergroup = self._member.membergroup if self._member else None
            self._membership = self._membergroup.membership if self._membergroup else None

    def get(self, compiler):
        return compiler.get(
            order=self._order,
            payment_method=self._payment_method,
            delivery_method=self._delivery_method,
            shipping_address=self._shipping_address,
            sej_order=self.sej_order,
            user=self._user,
            member=self._member,
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

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf')
    parser.add_argument('--verbose', action='store_true', default=False)
    opts = parser.parse_args(argv)

    if not opts.verbose:
        pyramid.paster.setup_logging(opts.conf)

    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings
    request = pyramid.testing.DummyRequest()
    session = altair.sqlahelper.get_db_session(request, 'slave')

    import json
    import collections

    req_str = '''{
        "Order.id": [],
        "Order.order_no": [],
        "Order.created_at": [],
        "Order.paid_at": [],
        "Order.delivered_at": [],
        "Order.canceled_at": [],
        "Order.refunded_at": [],
        "ShippingAddress.created_at": ["2014-01-01-00-00-00", null],
        "OrderedProduct.price": []
    }'''

    column_compiler = {
        "Order.no": OrderOrderNoCompiler,
        "Order.status": OrderStatusCompiler,
        "Order.payment_status": OrderPaymentStatusCompiler,
        "Order.created_at": OrderCreatedAtCompiler,
        "Order.paid_at": OrderCreatedAtCompiler,
        "Order.delivered_at": OrderDeliveredAtCompiler,
        "Order.canceled_at": OrderCanceledAtCompiler,
        "Lot.name": LotNameCompiler,
        "Order.total_amount": OrderTotalAmountCompiler,
        "Order.transaction_fee": OrderTransactionFeeCompiler,
        "Order.delivery_fee": OrderDeliveryFeeCompiler,
        "Order.system_fee": OrderSystemFeeCompiler,
        "Order.special_fee": OrderSpecialFeeCompiler,
        "Margin": MarginCompiler,
        "Order.refund_total_amount": OrderRefundTotalAmountCompiler,
        "Order.refund_transaction_fee": OrderRefundTransactionFeeCompiler,
        "Order.refund_delivery_fee": OrderRefundDeliveryFeeCompiler,
        "Order.refund_system_fee": OrderRefundSystemFeeCompiler,
        "Order.refund_special_fee": OrderRefundSpecialFeeCompiler,
        "Order.note": OrderNoteCompiler,
        "Order.special_fee_name": OrderSpecialFeeNameCompiler,
        "Order.card_brand": OrderCardBrandCompiler,
        "Order.card_ahead_com_code": OrderCardAHeadComCodeCompiler,
        "Order.card_ahead_com_name": OrderCardAHeadComNameCompiler,
        "SejOrder.ticketing_start_at": SejOrderTicketingStartAtCompiler,
        "SejOrder.ticketing_due_at": SejOrderTicketingDueAtCompiler,
        "SejOrder.pay_at": SejOrderPayAtCompiler,
        "SejOrder.payment_due_at": SejOrderPaymentDueAtCompiler,
        "SejOrder.billing_number": SejOrderBillingNumberCompiler,
        "SejOrder.exchange_number": SejOrderExchangeNumberCompiler,
        "MailMagazine.permission": MailMagazinePermissionCompiler,
        "UserProfile.last_name": UserProfileLastNameCompiler,
        "UserProfile.first_name": UserProfileFirstNameCompiler,
        "UserProfile.last_name_kana": UserProfileLastNameKANACompiler,
        "UserProfile.first_name_kana": UserProfileFirstNameKANACompiler,
        "UserProfile.nick_name": UserProfileNickNameCompiler,
        "UserProfile.sex": UserProfileSexCompiler,
        "Membership.name": MembershipNameCompiler,
        "MemberGroup.name": MemberGroupNameCompiler,
        "UserCredential.auth_identifier": UserCredentialAuthIdentiferCompiler,
        "ShippingAddress.last_name": ShippingAddressLastNameCompiler,
        "ShippingAddress.first_name": ShippingAddressFirstNameCompiler,
        "ShippingAddress.last_name_kana": ShippingAddressLastNameKANACompiler,
        "ShippingAddress.first_name_kana": ShippingAddressFirstNameKANACompiler,
        "ShippingAddress.zip": ShippingAddressZipCompiler,
        "ShippingAddress.country": ShippingAddressCountryCompiler,
        "ShippingAddress.prefecture": ShippingAddressPrefectureCompiler,
        "ShippingAddress.city": ShippingAddressCityCompiler,
        "ShippingAddress.address_1": ShippingAddressAddress1Compiler,
        "ShippingAddress.address_2": ShippingAddressAddress2Compiler,
        "ShippingAddress.tel_1": ShippingAddressTel1Compiler,
        "ShippingAddress.tel_2": ShippingAddressTel2Compiler,
        "ShippingAddress.fax": ShippingAddressFaxCompiler,
        "ShippingAddress.email_1": ShippingAddressEmail1Compiler,
        "ShippingAddress.email_2": ShippingAddressEmail2Compiler,
        "PaymentMethod.name": PaymentMethodNameCompiler,
        "DeliveryMethod.name": DeliveryMethodNameCompiler,
        "Event.title": EventTitleCompiler,
        "Performance.name": PerformanceNameCompiler,
        "Performance.code": PerformanceCodeCompiler,
        "Performance.start_on": PerformanceStartOnCompiler,
        "Venue.name": VenueNameCompiler,
        "Order.product_count": OrderProductCountCompiler,
        }

    decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
    req = decoder.decode(req_str)

    # compilers = [columns[name] for name in req.keys()]
    # entities = [compiler.entity for compiler in compilers]
    organization_id = 15

    qs = session.query(Order)
    qs = qs\
      .outerjoin(ShippingAddress)\
      .outerjoin(OrderedProduct)\
      .outerjoin(PaymentDeliveryMethodPair)\
      .outerjoin(PaymentMethod)\
      .outerjoin(DeliveryMethod)\
      .outerjoin(OrderedProductItem)\
      .outerjoin(User, Order.user_id==User.id)\
      .outerjoin(Member)\
      .outerjoin(MemberGroup)\
      .outerjoin(Membership)\
      .filter(Order.organization_id==organization_id)

    from sqlalchemy.orm import joinedload
    qs = qs.options(joinedload('shipping_address'))
    qs = qs.options(joinedload('user'))
    qs = qs.options(joinedload('user.member'))
    qs = qs.options(joinedload('user.member.membergroup'))
    qs = qs.options(joinedload('user.member.membergroup.membership'))

    # qs = qs.with_entities(*entities)
    # for name, values in req.items():
    #     compiler = columns[name]
    #     qs = compiler.compile(qs, *values)

    qs = qs.order_by(sqlalchemy.desc(Order.id))
    qs = qs.limit(10000)
    _bench(datetime.datetime.now())
    _bench('GET ORDERS')
    orders = qs.all()

    # def _f(order):
    #     if order.payment_delivery_pair.payment_method.payment_plugin_id == 3:
    #         sej_order = order.sej_order
    #         if sej_order:
    #             return sej_order.billing_number
    _bench('CREATE ORDER_NO LIST')
    order_nos = [order.order_no for order in orders]

    _bench('GET SEJ ORDERS')
    sej_orders = session\
        .query(SejOrder)\
        .filter(SejOrder.order_no.in_(order_nos))\
        .all()

    _bench('ORDER_NO SEJORDE DICTIONARY START')
    orderno_sejorder = dict((sej_order.order_no, sej_order) for sej_order in sej_orders)

    _bench('MAIL PERMISSION START')
    qs = session\
      .query(MailSubscription)\
      .filter(MailSubscription.segment_id==MailMagazine.id)\
      .filter(or_(MailSubscription.status==None, MailSubscription.status==MailSubscriptionStatus.Subscribed.v))\
      .filter(MailMagazine.organization_id==organization_id)\
      .with_entities(MailSubscription.email)
    subscribed_emails = set(elms[0] for elms in qs)

    _bench('LOT START')
    qs = session\
      .query(LotEntry)\
      .filter(LotEntry.entry_no.in_(order_nos))
    orderno_lotentry = dict((lot_entry.entry_no, lot_entry) for lot_entry in qs)

    _bench('CREATE ADAPTERS')
    adapters = [OrderExportAdapter(order, orderno_sejorder, subscribed_emails, orderno_lotentry) for order in orders]
    _bench('FINISH CREATE ADAPTERS')
    _bench(len(sej_orders))
    #[orderno_sejorder.get(order.order_no, None) for order in adapters]
    _bench('CREATE REQUEST COLUMN')
    request_columns = [key for key, value in column_compiler.items() if value]
    _bench('CREATE COMPILER LIST')
    compilers = [column_compiler[column] for column in request_columns]
    _bench('CREATE LIST FOR CSV') # ココが時間がかかる
    header = [compiler.name.encode('cp932') for compiler in compilers]
    rows = tuple(
        tuple(unicode(adapter.get(compiler)).encode('cp932') for compiler in compilers)
        for adapter in adapters
        )
    _bench('CREATE CSV')
    import csv
    fp = io.StringIO()
    writer = csv.writer(fp)
    _bench('WRITE CSV')
    writer.writerow(header)
    writer.writerows(rows)
    _bench('WRITE FILE')
    fp.seek(0)
    dp = open('/Users/takeshishimada/tmp/test.csv', 'w+b')
    dp.write(fp.read())
    dp.close()
    _bench('FINISH')

    # qs = session\
    #   .query(Order)\
    #   .join(Organization)\
    #   .filter(Order.created_at>datetime.datetime.strptime('20130101', '%Y%m%d'))\
    #   .limit(100000)
    # print str(qs)
    #
    # import csv
    # fp = io.StringIO()
    # writer = csv.writer(fp)
    # print str(qs)
    # _bench('A')
    # datas = qs.all()
    # _bench('B')
    # writer.writerows(datas)
    # _bench('C')
    # for data in datas[:10]:
    #     print data
    # _bench('D')

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
