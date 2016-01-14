#-*- encoding: utf-8 -*-
import logging
import itertools
from datetime import datetime, timedelta
import sqlalchemy as sa
import sqlalchemy.event
import sqlalchemy.orm.collections
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.exc import (
    MultipleResultsFound,
    NoResultFound,
    )
from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import exists, desc, select, case, null
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from pyramid.decorator import reify
from pyramid.threadlocal import get_current_request
from zope.interface import implementer
from zope.deprecation import deprecation
from dateutil.parser import parse as parsedate

from altair.sqla import session_partaken_by, HybridRelation
from altair.models import WithTimestamp, LogicallyDeleted, MutationDict, JSONEncodedDict, Identifier

from altair.app.ticketing.payments import plugins
from altair.app.ticketing.utils import StandardEnum
from altair.app.ticketing.models import BaseModel
from altair.app.ticketing.core.exceptions import InvalidStockStateError
from altair.app.ticketing.core.interfaces import (
    IOrderLike,
    IOrderedProductLike,
    IOrderedProductItemLike,
    )
from altair.app.ticketing.core.models import (
    Organization,
    ShippingAddress,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    Event,
    Performance,
    Venue,
    StockStatus,
    Seat,
    SeatStatus,
    Refund,
    ShippingAddressMixin,
    ChannelEnum,
    SeatStatusEnum,
    SalesSegment,
)
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    Member,
    MemberGroup,
    Membership,
    UserCredential,
    UserPointAccount,
)
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )
from altair.app.ticketing.models import (
    Base,
)
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.sej import api as sej_api

logger = logging.getLogger(__name__)


class SummarizedUser(object):
    def __init__(self, session, id, membership_id, membergroup_id, user_profile):
        self.session = session
        self.id = id
        self.membership_id = membership_id
        self.membergroup_id = membergroup_id
        self.user_profile = user_profile

    @reify
    def _user_credential_member_pairs(self):
        return self.session.query(UserCredential, Member) \
            .outerjoin(Member,
                and_(
                    Member.auth_identifier == UserCredential.auth_identifier,
                    Member.membership_id == self.membership_id,
                    Member.membergroup_id == self.membergroup_id
                    )
                ) \
            .filter(UserCredential.user_id == self.id) \
            .distinct() \
            .all()

    @reify
    def user_credential(self):
        return self._user_credential_member_pairs[0][0] if len(self._user_credential_member_pairs) > 0 else None

    @reify
    def member(self):
        return self._user_credential_member_pairs[0][1] if len(self._user_credential_member_pairs) > 0 else None


class SummarizedMembership(object):
    def __init__(self, name):
        self.name = name

class SummarizedMemberGroup(object):
    def __init__(self, name):
        self.name = name

class SummarizedUserProfile(object):
    def __init__(self,
                 last_name,
                 first_name,
                 last_name_kana,
                 first_name_kana,
                 nick_name,
                 sex,):
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.nick_name = nick_name
        self.sex = sex

class SummarizedPaymentMethod(object):
    def __init__(self, payment_plugin_id, name):
        self.payment_plugin_id = payment_plugin_id
        self.name = name

class SummarizedDeliveryMethod(object):
    def __init__(self, delivery_plugin_id, name):
        self.delivery_plugin_id = delivery_plugin_id
        self.name = name

class SummarizedPaymentDeliveryMethodPair(object):
    def __init__(self, payment_method, delivery_method):
        self.payment_method = payment_method
        self.delivery_method = delivery_method

class SummarizedEvent(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title

class SummarizedVenue(object):
    def __init__(self, name):
        self.name = name

class SummarizedPerformance(object):
    def __init__(self, id, name, code, start_on, event, venue):
        self.id = id
        self.name = name
        self.code = code
        self.start_on = start_on
        self.event = event
        self.venue = venue

class SummarizedShippingAddress(ShippingAddressMixin):
    def __init__(self, last_name, first_name, last_name_kana, first_name_kana, zip, country, prefecture, city, address_1, address_2, tel_1, tel_2, fax, email_1, email_2):
        self.last_name = last_name
        self.first_name = first_name
        self.last_name_kana = last_name_kana
        self.first_name_kana = first_name_kana
        self.zip = zip
        self.country = country
        self.prefecture = prefecture
        self.city = city
        self.tel_1 = tel_1
        self.tel_2 = tel_2
        self.address_1 = address_1
        self.address_2 = address_2
        self.fax = fax
        self.email_1 = email_1
        self.email_2 = email_2

def _get_performances(request, organization_id):
    if not hasattr(request, "_performances"):
        results = sa.select(
            [
                Event.id.label("event_id"),
                Event.title,
                Performance.id.label('performance_id'),
                Performance.name.label('performance_name'),
                Performance.code,
                Performance.start_on,
                Venue.name.label('venue_name'),
            ],
            Event.organization_id==organization_id,
            from_obj=[
                Performance.__table__.join(
                    Event.__table__,
                ).join(
                    Venue.__table__,
                )]).execute()

        performances = {}
        for row in results:
            performances[row.performance_id] = SummarizedPerformance(
                row.performance_id,
                row.performance_name,
                row.code,
                row.start_on,
                SummarizedEvent(
                    row.event_id,
                    row.title
                    ),
                SummarizedVenue(row.venue_name)
                )
        request._performances = performances
    return request._performances

def _get_performance(request, performance_id, organization_id):
    performances = _get_performances(request, organization_id)
    return performances[performance_id]


class OrderAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderAttribute"
    order_id  = sa.Column(Identifier, sa.ForeignKey('Order.id'), primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(255), primary_key=True, nullable=False)
    value = sa.Column(sa.Unicode(1023))

class OrderedProductAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderedProductAttribute"
    ordered_product_item_id  = sa.Column(Identifier, sa.ForeignKey('OrderedProductItem.id'), primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(255), primary_key=True, nullable=False)
    value = sa.Column(sa.Unicode(1023))

class OrderCancelReasonEnum(StandardEnum):
    User = (1, u'お客様都合')
    Promoter = (2, u'主催者都合')
    CallOff = (3, u'中止')

# TODO: OrderedProductItemToken に統合する
orders_seat_table = sa.Table("orders_seat", Base.metadata,
    sa.Column("seat_id", Identifier, sa.ForeignKey("Seat.id")),
    sa.Column("OrderedProductItem_id", Identifier, sa.ForeignKey("OrderedProductItem.id"))
)


order_user_point_account_table = sa.Table(
    "Order_UserPointAccount", Base.metadata,
    sa.Column("order_id", Identifier, sa.ForeignKey("Order.id")),
    sa.Column("user_point_account_id", Identifier, sa.ForeignKey("UserPointAccount.id"))
    )

@implementer(IOrderLike)
class Order(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Order'
    __table_args__= (
        sa.UniqueConstraint('order_no', 'branch_no', name="ix_Order_order_no_branch_no"),
        )
    __clone_excluded__ = ['cart', 'ordered_from', 'payment_delivery_pair', 'performance', 'user', '_attributes', 'refund', 'operator', 'lot_entries', 'lot_wishes', 'point_grant_history_entries', 'sales_segment', 'order_notification', 'proto_order', 'membership', 'membergroup', 'cart_setting']

    id = sa.Column(Identifier, primary_key=True)
    user_id = sa.Column(Identifier, sa.ForeignKey("User.id"))
    user = orm.relationship('User')
    shipping_address_id = sa.Column(Identifier, sa.ForeignKey("ShippingAddress.id"))
    shipping_address = orm.relationship('ShippingAddress', backref='order')
    organization_id = sa.Column(Identifier, sa.ForeignKey("Organization.id"))
    ordered_from = orm.relationship('Organization', backref='orders')
    operator_id = sa.Column(Identifier, sa.ForeignKey("Operator.id"))
    operator = orm.relationship('Operator', uselist=False)
    channel = sa.Column(sa.Integer, nullable=True)

    total_amount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    system_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    transaction_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    special_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)
    special_fee_name = sa.Column(sa.Unicode(255), nullable=False, default=u"")

    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair", backref='orders')

    @property
    def payment_delivery_method_pair(self):
        return self.payment_delivery_pair

    paid_at = sa.Column(sa.DateTime, nullable=True, default=None)
    delivered_at = sa.Column(sa.DateTime, nullable=True, default=None)
    canceled_at = sa.Column(sa.DateTime, nullable=True, default=None)
    refund_id = sa.Column(Identifier, sa.ForeignKey('Refund.id'))
    refunded_at = sa.Column(sa.DateTime, nullable=True, default=None)
    released_at = sa.Column(sa.DateTime, nullable=True, default=None)

    order_no = sa.Column(sa.Unicode(255))
    branch_no = sa.Column(sa.Integer, nullable=False, default=1, server_default='1')
    note = sa.Column(sa.UnicodeText, nullable=True, default=None)

    issued = sa.Column(sa.Boolean, nullable=False, default=False)
    issued_at = sa.Column(sa.DateTime, nullable=True, default=None, doc=u"印刷可能な情報伝達済み")
    printed_at = sa.Column(sa.DateTime, nullable=True, default=None, doc=u"実発券済み")

    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))
    performance = orm.relationship('Performance', backref="orders")

    _attributes = orm.relationship("OrderAttribute", backref='order', collection_class=orm.collections.attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderAttribute(name=k, value=v))

    cart_setting_id = sa.Column(Identifier, sa.ForeignKey('CartSetting.id'), nullable=True)
    cart_setting = declared_attr(lambda self: orm.relationship('CartSetting'))

    membership_id = sa.Column(Identifier, sa.ForeignKey('Membership.id'), nullable=True)
    membership = orm.relationship('Membership')
    membergroup_id = sa.Column(Identifier, sa.ForeignKey('MemberGroup.id'), nullable=True)
    membergroup = orm.relationship('MemberGroup')

    user_point_accounts = orm.relationship('UserPointAccount', secondary=order_user_point_account_table)

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_multicheckout_info()を使ってほしい")
    def multicheckout_info(self):
        from .api import get_multicheckout_info
        request = get_current_request()
        return get_multicheckout_info(request, self)

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_multicheckout_info()を使ってほしい")
    def card_brand(self):
        return self.multicheckout_info and self.multicheckout_info['card_brand']

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_multicheckout_info()を使ってほしい")
    def card_ahead_com_code(self):
        return self.multicheckout_info and self.multicheckout_info['ahead_com_cd']

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_multicheckout_info()を使ってほしい")
    def card_ahead_com_name(self):
        return self.multicheckout_info and self.multicheckout_info['ahead_com_name']

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_multicheckout_info()を使ってほしい")
    def multicheckout_approval_no(self):
        return self.multicheckout_info and self.multicheckout_info['approval_no']

    fraud_suspect = sa.Column(sa.Boolean, nullable=True, default=None)
    browserid = sa.Column(sa.Unicode(40))

    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref='orders')

    issuing_start_at = sa.Column(sa.DateTime, nullable=True)
    issuing_end_at   = sa.Column(sa.DateTime, nullable=True)
    payment_start_at = sa.Column(sa.DateTime, nullable=True)
    payment_due_at   = sa.Column(sa.DateTime, nullable=True)

    refund_total_amount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)
    refund_system_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)
    refund_transaction_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)
    refund_delivery_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)
    refund_special_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)

    manual_point_grant = sa.Column(sa.Boolean, nullable=False, default=False)

    @property
    def organization(self):
        return self.ordered_from

    @property
    def ordered_products(self):
        return self.items

    @ordered_products.setter
    def ordered_products(self, value):
        self.items = value

    ordered_products = deprecation.deprecated(ordered_products, 'use items property instead')

    def is_canceled(self):
        return bool(self.canceled_at)

    def is_issued(self):
        """
        チケット券面が発行済みかどうかを返す。
        Order, OrderedProductItem, OrderedProductItemTokenという階層中にprinted_atが存在。
        """
        if self.issued_at:
            return True

        qs = OrderedProductItem.query.filter_by(deleted_at=None)\
            .filter(OrderedProduct.order_id==self.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProductItem.issued_at==None)
        return qs.first() is None

    def is_printed(self):
        """
        チケット券面が印刷済みかどうかを返す。(順序としてはissued -> printed)

        Order, OrderedProductItem, OrderedProductItemTokenという階層中にprinted_atが存在。
        各下位オブジェクトが全てprintedであれば、printed = True
        """
        if self.printed_at:
            return True

        qs = OrderedProductItem.query.filter_by(deleted_at=None)\
            .filter(OrderedProduct.order_id==self.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProductItem.printed_at==None)
        return qs.first() is None

    def deliver_at_store(self):
        """
        コンビニ受取かどうかを判定する。
        """
        return self.payment_delivery_pair.delivery_method.deliver_at_store()

    @property
    def created_from_lot_entry(self):
        from altair.app.ticketing.lots.models import LotEntry
        return orm.session.object_session(self).query(LotEntry).join(LotEntry.lot).filter(LotEntry.entry_no == self.order_no).first()

    @classmethod
    def __declare_last__(cls):
        from altair.app.ticketing.core.models import TicketPrintQueueEntry
        cls.queued = orm.column_property(
                exists(select('*') \
                    .select_from(TicketPrintQueueEntry.__table__ \
                        .join(OrderedProductItem.__table__) \
                        .join(OrderedProduct.__table__)) \
                    .where(OrderedProduct.order_id==cls.id) \
                    .where(TicketPrintQueueEntry.processed_at==None)),
                deferred=True)

    @classmethod
    def inner_channels(cls):
        return [ChannelEnum.INNER.v, ChannelEnum.IMPORT.v]

    @property
    def payment_plugin_id(self):
        return self.payment_delivery_pair.payment_method.payment_plugin_id

    @property
    def delivery_plugin_id(self):
        return self.payment_delivery_pair.delivery_method.delivery_plugin_id

    @property
    @deprecation.deprecate(u"altair.app.ticketing.sej.api.get_sej_order()を使ってほしい")
    def sej_order(self):
        return sej_api.get_sej_order(self.order_no)

    @property
    def status(self):
        if self.canceled_at:
            return 'canceled'
        elif self.delivered_at:
            return 'delivered'
        elif self.deleted_at:
            return 'deleted'
        elif self.refunded_at:
            return 'refunded'
        else:
            return 'ordered'

    @property
    def payment_status(self):
        if self.refund_id and not self.refunded_at:
            return 'refunding'
        elif self.refunded_at:
            return 'refunded'
        elif self.paid_at:
            return 'paid'
        else:
            return 'unpaid'

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None

    @property
    def prev(self):
        from altair.app.ticketing.models import DBSession
        return DBSession.query(Order, include_deleted=True).filter_by(order_no=self.order_no).filter_by(branch_no=self.branch_no-1).one()

    @property
    @deprecation.deprecate(u"altair.app.ticketing.orders.api.get_anshin_checkout_object()を使ってほしい")
    def checkout(self):
        request = get_current_request()
        from .api import get_anshin_checkout_object
        return get_anshin_checkout_object(request, self)

    @property
    def is_inner_channel(self):
        return self.channel in self.inner_channels()

    def payment_status_changable(self, status):
        if status == 'paid':
            if self.payment_status == 'paid':
                return True
            # 入金済への決済ステータスは窓口支払のみ変更可能
            return (self.status == 'ordered' and self.payment_status == 'unpaid' and self.payment_delivery_pair.payment_method.payment_plugin_id == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID)
        elif status == 'unpaid':
            if self.payment_status == 'unpaid':
                return True
            # 未入金への決済ステータスは、窓口支払もしくはインナー予約のみ変更可能
            return (self.status == 'ordered' and self.payment_status == 'paid' and (self.payment_delivery_pair.payment_method.payment_plugin_id ==  plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID or self.is_inner_channel))
        else:
            return False

    def can_cancel(self):
        # 受付済のみキャンセル可能、払戻時はキャンセル不可
        if self.status == 'ordered' and self.payment_status in ('unpaid', 'paid'):
            # コンビニ決済は未入金のみキャンセル可能
            payment_plugin_id = self.payment_delivery_pair.payment_method.payment_plugin_id
            if payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID and self.payment_status != 'unpaid':
                return False
            # コンビニ引取は未発券のみキャンセル可能
            delivery_plugin_id = self.payment_delivery_pair.delivery_method.delivery_plugin_id
            if delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID and self.is_issued():
                return False
            return True
        return False

    def can_refund(self):
        # 入金済または払戻予約のみ払戻可能
        return (self.status in ['ordered', 'delivered'] and self.payment_status in ['paid', 'refunding'])

    def can_deliver(self):
        # 受付済のみ配送済に変更可能
        # インナー予約は常に、それ以外は入金済のみ変更可能
        return self.status == 'ordered' and (self.is_inner_channel or self.payment_status == 'paid')

    def can_delete(self):
        # キャンセルのみ論理削除可能
        return self.status == 'canceled'

    def can_release_stocks(self):
        # 払戻済のみ座席解放可能
        return (self.status == 'ordered' and self.payment_status == 'refunded' and self.released_at is None)

    def cancel(self, request, payment_method=None, now=None):
        from .api import refund_order, cancel_order
        try:
            if self.payment_status == 'refunding':
                refund_order(request, self, payment_method=payment_method, now=now)
            else:
                cancel_order(request, self, now=now)
        except Exception as e:
            logger.exception(u'キャンセルに失敗しました')
            return False
        return True

    def mark_canceled(self, now=None):
        self.canceled_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_refunded(self, now=None):
        self.refunded_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_delivered(self, now=None):
        self.delivered_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_paid(self, now=None):
        self.paid_at = now or datetime.now()

    def mark_released(self, now=None):
        self.released_at = now or datetime.now()

    def mark_issued_or_printed(self, issued=False, printed=False, now=None):
        if not issued and not printed:
            raise ValueError('either issued or printed must be True')

        if printed:
            if not (issued or self.issued):
                raise Exception('trying to mark an order as printed that has not been issued')

        now = now or datetime.now()
        delivery_plugin_id = self.payment_delivery_pair.delivery_method.delivery_plugin_id

        for ordered_product in self.items:
            for item in ordered_product.ordered_product_items:
                reissueable = item.product_item.ticket_bundle.reissueable(delivery_plugin_id)
                if issued:
                    if self.issued:
                        if not reissueable:
                            logger.warning("Trying to reissue a ticket for Order (id=%d) that contains OrderedProductItem (id=%d) associated with a ticket which is not marked reissueable" % (self.id, item.id))
                    item.issued = True
                    item.issued_at = now
                    for token in item.tokens:
                        token.issued_at = now
                if printed:
                    item.printed_at = now
                    for token in item.tokens:
                        token.printed_at = now
        if issued:
            self.issued = True
            self.issued_at = now
        if printed:
            self.printed_at = now


    @property
    def refund_per_order_fee(self):
        from altair.app.ticketing.orders.api import get_refund_per_order_fee
        return get_refund_per_order_fee(self.refund, self)

    @property
    def refund_per_ticket_fee(self):
        from altair.app.ticketing.orders.api import get_refund_per_ticket_fee
        return get_refund_per_ticket_fee(self.refund, self)

    def get_refund_ticket_price(self, product_item_id):
        from altair.app.ticketing.orders.api import get_refund_ticket_price
        return get_refund_ticket_price(
            self.refund,
            self,
            product_item_id
            )

    def get_item_refund_record(self, item):
        return item

    @staticmethod
    def reserve_refund(kwargs):
        refund = Refund(**kwargs)
        refund.save()
        return refund

    def call_refund(self, request):
        # 払戻金額を保存
        if self.refund.include_system_fee:
            self.refund_system_fee = self.system_fee
        if self.refund.include_special_fee:
            self.refund_special_fee = self.special_fee
        if self.refund.include_transaction_fee:
            self.refund_transaction_fee = self.transaction_fee
        if self.refund.include_delivery_fee:
            self.refund_delivery_fee = self.delivery_fee
        if self.refund.include_item:
            for ordered_product in self.items:
                ordered_product.refund_price = ordered_product.price
                for ordered_product_item in ordered_product.ordered_product_items:
                    ordered_product_item.refund_price = ordered_product_item.price
        refund_fee = self.refund_special_fee + self.refund_system_fee + self.refund_transaction_fee + self.refund_delivery_fee
        self.refund_total_amount = sum(o.refund_price * o.quantity for o in self.items) + refund_fee

        try:
            return self.cancel(request, self.refund.payment_method)
        except Exception:
            logger.exception(u'払戻処理でエラーが発生しました')
        return False

    def release(self):
        # 在庫を解放する
        for product in self.items:
            product.release()

    def change_payment_status(self, status):
        if self.payment_status_changable(status):
            if self.payment_status != status:
                if status == 'paid':
                    self.mark_paid()
                if status == 'unpaid':
                    self.paid_at = None
                self.save()
                return True
        return False

    @deprecation.deprecate(u"change_payment_statusを使ってほしい")
    def change_status(self, status):
        return self.change_payment_status(status)

    def delivered(self):
        if self.can_deliver():
            self.mark_delivered()
            self.save()
            return True
        else:
            return False

    def undelivered(self):
        self.delivered_at = None
        self.save()
        return True

    def delete(self, force=False):
        if not self.can_delete() and not force:
            logger.info('order (%s) cannot delete status (%s)' % (self.id, self.status))
            raise Exception(u'キャンセル以外は非表示にできません')

        # delete OrderedProduct
        for ordered_product in self.items:
            ordered_product.delete()

        # delete ShippingAddress
        if self.shipping_address:
            self.shipping_address.delete()

        super(Order, self).delete()

    @classmethod
    def clone(cls, origin, **kwargs):
        new_order = super(Order, cls).clone(origin, **kwargs)
        new_order.branch_no = origin.branch_no + 1
        new_order.attributes = origin.attributes
        new_order.created_at = origin.created_at
        for op, nop in itertools.izip(origin.items, new_order.items):
            for opi, nopi in itertools.izip(op.ordered_product_items, nop.ordered_product_items):
                nopi.seats = opi.seats
                nopi.attributes = opi.attributes

        new_order.add()
        origin.delete(force=True)
        return Order.get(new_order.id, new_order.organization_id)

    @staticmethod
    def get(id, organization_id, include_deleted=False):
        from altair.app.ticketing.models import DBSession
        query = DBSession.query(Order, include_deleted=include_deleted).filter_by(id=id, organization_id=organization_id)
        return query.first()

    @classmethod
    def create_from_cart(cls, cart):
        from altair.app.ticketing.models import DBSession
        order = cls(
            order_no=cart.order_no,
            total_amount=cart.total_amount,
            shipping_address=cart.shipping_address,
            payment_delivery_pair=cart.payment_delivery_pair,
            system_fee=cart.system_fee,
            special_fee_name=cart.special_fee_name,
            special_fee=cart.special_fee,
            transaction_fee=cart.transaction_fee,
            delivery_fee=cart.delivery_fee,
            performance=cart.performance,
            sales_segment=cart.sales_segment,
            organization_id=cart.sales_segment.sales_segment_group.event.organization_id,
            channel=cart.channel,
            operator=cart.operator,
            user=cart.user,
            issuing_start_at=cart.issuing_start_at,
            issuing_end_at=cart.issuing_end_at,
            payment_start_at=cart.payment_start_at,
            payment_due_at=cart.payment_due_at,
            cart_setting_id=cart.cart_setting_id,
            membership_id=cart.membership_id,
            membergroup_id=cart.membergroup_id,
            user_point_accounts=cart.user_point_accounts
            )

        for product in cart.items:
            # この ordered_product はコンストラクタに order を指定しているので
            # 勝手に order.ordered_products に追加されるから、append は不要
            ordered_product = OrderedProduct(
                order=order, product=product.product, price=product.product.price, quantity=product.quantity)
            for element in product.elements:
                ordered_product_item = OrderedProductItem(
                    ordered_product=ordered_product,
                    product_item=element.product_item,
                    price=element.product_item.price,
                    quantity=element.product_item.quantity * product.quantity,
                    seats=element.seats
                    )
                for i, seat in core_api.iterate_serial_and_seat(ordered_product_item):
                    token = OrderedProductItemToken(
                        serial = i,
                        seat = seat,
                        valid=True #valid=Falseの時は何時だろう？
                        )
                    ordered_product_item.tokens.append(token)
        DBSession.flush() # これとっちゃだめ
        return order

    def release_stocks(self):
        # 払戻済のみ座席解放可能
        if self.can_release_stocks():
            logger.info('try release stock (order_no=%s)' % self.order_no)
            self.release()
            self.mark_released()
            return True
        return False

    @staticmethod
    def filter_by_performance_id(id):
        performance = Performance.get(id)
        if not performance:
            return None

        return Order.filter_by(organization_id=performance.event.organization_id)\
            .join(Order.items)\
            .join(OrderedProduct.elements)\
            .join(OrderedProductItem.product_item)\
            .filter(ProductItem.performance_id==id)\
            .distinct()

    @classmethod
    def get_valid_by_order_no(cls, order_no, session=None):
        if session is None:
            from altair.app.ticketing.models import DBSession
            session = DBSession
        return session.query(cls).filter_by(order_no=order_no).one()

    def get_order_attribute_pair_pairs(self, request, include_undefined_items=False, for_=None, mode=None):
        from .api import get_order_attribute_pair_pairs
        return get_order_attribute_pair_pairs(request, self, include_undefined_items=include_undefined_items, for_=for_, mode=mode)


class OrderNotification(Base, BaseModel):
    __tablename__ = 'OrderNotification'
    __clone_excluded__ = ['id', 'order_id', 'order']

    id = sa.Column(Identifier, primary_key=True)
    order_id = sa.Column(Identifier, sa.ForeignKey("Order.id", ondelete='CASCADE'), nullable=False, unique=True)
    payment_remind_at = sa.Column(sa.DateTime(), nullable=True) # SEJ 支払い期限リマインドメール送信日時
    print_remind_at = sa.Column(sa.DateTime(), nullable=True)

    order = orm.relationship('Order', backref=orm.backref('order_notification', uselist=False))


@sqlalchemy.event.listens_for(Order, 'after_insert')
def create_order_notification(mapper, connection, order):
    """Orderが作成されたタイミングでOrderNotificationも作成する
    """
    from altair.app.ticketing.models import DBSession
    order_notification = None
    before_order = None

    # branch_noが1っこ前のorderがあればそれの通知状態を引き継ぐ
    try:
        before_order = order.prev
    except NoResultFound as err:
        pass
    except MultipleResultsFound as err:
        assert False, '!? multiple order'

    if before_order and before_order.order_notification:
        order_notification = OrderNotification.clone(before_order.order_notification, deep=True)
    else:
        order_notification = OrderNotification()

    order_notification.order_id = order.id
    DBSession.add(order_notification)


@implementer(IOrderedProductLike)
class OrderedProduct(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProduct'
    __clone_excluded__ = ['order_id', 'product']

    id = sa.Column(Identifier, primary_key=True)
    order_id = sa.Column(Identifier, sa.ForeignKey("Order.id"))
    order = orm.relationship('Order', backref='items')
    proto_order_id = sa.Column(Identifier, sa.ForeignKey("ProtoOrder.id"))
    proto_order = orm.relationship('ProtoOrder', backref='items')
    product_id = sa.Column(Identifier, sa.ForeignKey("Product.id"))
    product = orm.relationship('Product', backref='ordered_products')
    price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    quantity = sa.Column(sa.Integer)
    refund_price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)


    @reify
    def current_order(self):
        order = None
        if self.order:
            order = self.order
        elif self.proto_order:
            order = Order.query.filter(Order.order_no==self.proto_order.order_no).first()
        return order

    @property
    def ordered_product_items(self):
        return self.elements

    @ordered_product_items.setter
    def ordered_product_items(self, value):
        self.elements = value

    ordered_product_items = deprecation.deprecated(ordered_product_items, 'use elements property instead')

    @property
    def seats(self):
        import operator
        return sorted(itertools.chain.from_iterable(i.seatdicts for i in self.ordered_product_items),
            key=operator.itemgetter('l0_id'))

    @property
    def seat_quantity(self):
        quantity = 0
        for element in self.elements:
            if element.product_item.stock_type.is_seat:
                quantity += element.quantity
        return quantity

    def release(self):
        # 在庫を解放する
        for element in self.elements:
            element.release()

    def delete(self):
        # delete OrderedProductItem
        for element in self.elements:
            element.delete()

        super(OrderedProduct, self).delete()

    def get_element_refund_record(self, element):
        return element


@implementer(IOrderedProductItemLike)
class OrderedProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProductItem'
    __clone_excluded__ = ['ordered_product_id', 'product_item', 'seats', '_attributes', 'print_histories']

    id = sa.Column(Identifier, primary_key=True)
    ordered_product_id = sa.Column(Identifier, sa.ForeignKey("OrderedProduct.id"))
    ordered_product = orm.relationship('OrderedProduct', backref='elements')
    product_item_id = sa.Column(Identifier, sa.ForeignKey("ProductItem.id"))
    product_item = orm.relationship('ProductItem', backref='ordered_product_items')
    issued_at = sa.Column(sa.DateTime, nullable=True, default=None)
    printed_at = sa.Column(sa.DateTime, nullable=True, default=None)
    seats = orm.relationship("Seat", secondary=orders_seat_table, backref='ordered_product_items')
    price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    refund_price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)

    _attributes = orm.relationship("OrderedProductAttribute", backref='ordered_product_item', collection_class=orm.collections.attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderedProductAttribute(name=k, value=v))

    # 実際の購入数
    quantity = sa.Column(sa.Integer, nullable=False, default=1, server_default='1')

    @property
    def seat_statuses_for_update(self):
        from altair.app.ticketing.models import DBSession
        if len(self.seats) > 0:
            # although seat_id is the primary key, optimizer may wrongly choose other index
            # if IN predicate has many values, because of implicit "deleted_at IS NULL" (#11358)
            return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats]))\
                .with_hint(SeatStatus, 'USE INDEX (primary)').with_lockmode('update').all()
        return []

    @property
    def name(self):
        if not self.seats:
            return u""
        return u', '.join([(seat.name) for seat in self.seats if seat.name])

    @property
    def seat_statuses(self):
        """ 確保済の座席ステータス
        """
        from altair.app.ticketing.models import DBSession
        return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).all()

    def release(self):
        # 座席開放
        cancellable_status = [
            int(SeatStatusEnum.Ordered),
            int(SeatStatusEnum.Reserved),
        ]
        for seat_status in self.seat_statuses_for_update:
            logger.info('trying to release seat (id=%d)' % seat_status.seat_id)
            if seat_status.status not in cancellable_status:
                logger.info('not releasing OrderedProductItem (id=%d, seat_id=%d, status=%d) for safety' % (self.id, seat_status.seat_id, seat_status.status))
                raise InvalidStockStateError("Order %s is associated with a seat (id=%d, status=%d) that is not marked ordered" % (self.ordered_product.order.order_no, seat_status.seat_id, seat_status.status))
            else:
                logger.info('setting status of seat (id=%d, status=%d) to Vacant (%d)' % (seat_status.seat_id, seat_status.status, int(SeatStatusEnum.Vacant)))
                seat_status.status = int(SeatStatusEnum.Vacant)

        # 在庫数を戻す
        if self.product_item.stock.stock_type.quantity_only:
            release_quantity = self.quantity
        else:
            release_quantity = len(self.seats)
        stock_status = StockStatus.filter_by(stock_id=self.product_item.stock_id).with_lockmode('update').one()
        logger.info('restoring the quantity of stock (id=%s, quantity=%d) by +%d' % (stock_status.stock_id, stock_status.quantity, release_quantity))
        stock_status.quantity += release_quantity
        stock_status.save()
        logger.info('done for OrderedProductItem (id=%d)' % self.id)

    @property
    def seatdicts(self):
        return ({'name': s.name, 'l0_id': s.l0_id}
                for s in self.seats)

    def is_issued(self):
        return self.issued_at or self.tokens == [] or all(token.issued_at for token in self.tokens)

    def is_printed(self):
        return self.printed_at or self.tokens == [] or self.exact_printed()

    def exact_printed(self):
        for token in self.tokens:
            if not token.is_printed():
                return False
        return True

    @property
    def issued_at_status(self):
        total = len(self.tokens)
        issued_count = len([i for i in self.tokens if i.issued_at])
        return dict(issued=issued_count, total=total)

    @property
    def printed_at_status(self):
        total = len(self.tokens)
        printed_count = len([i for i in self.tokens if i.is_printed()])
        return dict(printed=printed_count, total=total)

    def iterate_serial_and_seat(self):
        return core_api.iterate_serial_and_seat(self)


class OrderedProductItemToken(Base,BaseModel, LogicallyDeleted):
    __tablename__ = "OrderedProductItemToken"
    __clone_excluded__ = ['seat']

    id = sa.Column(Identifier, primary_key=True)
    ordered_product_item_id = sa.Column(Identifier, sa.ForeignKey("OrderedProductItem.id", ondelete="CASCADE"), nullable=False)
    item = orm.relationship("OrderedProductItem", backref="tokens")
    seat_id = sa.Column(Identifier, sa.ForeignKey("Seat.id", ondelete='CASCADE'), nullable=True)
    seat = orm.relationship("Seat", backref="tokens")
    serial = sa.Column(sa.Integer, nullable=False)
    key = sa.Column(sa.Unicode(255), nullable=True)    #今は使っていない。https://dev.ticketstar.jp/redmine/altair/issues/499#note-15
    valid = sa.Column(sa.Boolean, nullable=False, default=False)
    issued_at = sa.Column(sa.DateTime, nullable=True, default=None)
    printed_at = sa.Column(sa.DateTime, nullable=True, default=None)
    refreshed_at = sa.Column(sa.DateTime, nullable=True, default=None)

    def is_printed(self):
        return self.printed_at and (self.refreshed_at is None or self.printed_at > self.refreshed_at)


class ImportStatusEnum(StandardEnum):
    ConfirmNeeded = 0
    Waiting = 1
    Importing = 2
    Imported = 3
    Aborted = 4


class ImportTypeEnum(StandardEnum):
    Create = 1             # BITMASK
    Update = 2             # BITMASK
    CreateOrUpdate = 3     # BITMASK
    AlwaysIssueOrderNo = 4 # BITMASK


class AllocationModeEnum(StandardEnum):
    AlwaysAllocateNew = 1
    NoAutoAllocation = 2

class OrderImportTask(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderImportTask'

    id = sa.Column(Identifier, primary_key=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id', ondelete='CASCADE'), nullable=False)
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'), nullable=True)
    operator_id = sa.Column(Identifier, sa.ForeignKey('Operator.id', ondelete='CASCADE'), nullable=False)
    import_type = sa.Column(sa.Integer, nullable=False)
    allocation_mode = sa.Column(sa.Integer, default=1, nullable=False) # XXX: 1 = AllocationModeEnum.AlwaysAllocateNew
    entrust_separate_seats = sa.Column(sa.Boolean, default=False, nullable=False)
    merge_order_attributes = sa.Column(sa.Boolean, default=False, nullable=False)
    status = sa.Column(sa.Integer, nullable=False)
    count = sa.Column(sa.Integer, nullable=False)
    data = sa.Column(sa.UnicodeText(8388608))
    errors = sa.Column(MutationDict.as_mutable(JSONEncodedDict(65536)), nullable=True)

    organization = orm.relationship('Organization')
    performance = orm.relationship('Performance')
    operator = orm.relationship('Operator')

proto_order_user_point_account_table = sa.Table(
    "ProtoOrder_UserPointAccount", Base.metadata,
    sa.Column("proto_order_id", Identifier, sa.ForeignKey("ProtoOrder.id")),
    sa.Column("user_point_account_id", Identifier, sa.ForeignKey("UserPointAccount.id"))
    )

@implementer(IOrderLike)
class ProtoOrder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ProtoOrder'
    __table_args__ = (
        sa.UniqueConstraint('ref', 'order_import_task_id', name='ix_ref_order_import_task_id'),
        )

    id = sa.Column(Identifier, primary_key=True)
    ref = sa.Column(sa.Unicode(255), nullable=True)
    order_no = sa.Column(sa.Unicode(255), nullable=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey("Organization.id"))
    organization = orm.relationship('Organization')
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))
    performance = orm.relationship('Performance')
    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment')
    user_id = sa.Column(Identifier, sa.ForeignKey("User.id"))
    user = orm.relationship('User')
    shipping_address_id = sa.Column(Identifier, sa.ForeignKey("ShippingAddress.id"))
    shipping_address = orm.relationship('ShippingAddress')
    operator_id = sa.Column(Identifier, sa.ForeignKey("Operator.id"))
    operator = orm.relationship('Operator', uselist=False)

    total_amount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=True)
    system_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=True)

    special_fee_name = sa.Column(sa.Unicode(255), nullable=True)
    special_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=True)
    transaction_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=True)
    delivery_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=True)


    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair")

    note = sa.Column(sa.UnicodeText, nullable=True, default=None)

    attributes = orm.deferred(sa.Column(MutationDict.as_mutable(JSONEncodedDict(16384))))

    issuing_start_at = sa.Column(sa.DateTime, nullable=True)
    issuing_end_at   = sa.Column(sa.DateTime, nullable=True)
    payment_start_at = sa.Column(sa.DateTime, nullable=True)
    payment_due_at   = sa.Column(sa.DateTime, nullable=True)
    processed_at     = sa.Column(sa.DateTime, nullable=True)

    original_lot_entry_id = sa.Column(Identifier, sa.ForeignKey('LotEntry.id'), nullable=True)
    original_lot_entry = orm.relationship('LotEntry')

    original_order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'), nullable=True)
    original_order = orm.relationship('Order')

    order_import_task_id = sa.Column(Identifier, sa.ForeignKey('OrderImportTask.id'), nullable=True)
    order_import_task = orm.relationship('OrderImportTask', backref=orm.backref('proto_orders', order_by='ProtoOrder.id'))

    new_order_created_at = sa.Column(sa.TIMESTAMP, nullable=True, default=None)
    new_order_paid_at = sa.Column(sa.DateTime, nullable=True, default=None)

    cart_setting_id = sa.Column(Identifier, nullable=True)

    membership_id = sa.Column(Identifier, sa.ForeignKey('Membership.id'), nullable=True)
    membership = orm.relationship('Membership')

    membergroup_id = sa.Column(Identifier, sa.ForeignKey('MemberGroup.id'), nullable=True)
    membergroup = orm.relationship('MemberGroup')

    user_point_accounts = orm.relationship('UserPointAccount', secondary=proto_order_user_point_account_table)

    def mark_processed(self, now=None):
        self.processed_at = now or datetime.now()

    @classmethod
    def create_from_order_like(cls, order_like):
        note = getattr(order_like, 'note', None)
        attributes = dict(getattr(order_like, 'attributes', {}))

        def build_element(element):
            retval = OrderedProductItem(
                product_item=element.product_item,
                price=element.price,
                quantity=element.product_item.quantity * item.quantity,
                seats=element.seats,
                attributes=dict(element.attributes) if hasattr(element, 'attributes') else {}
                )
            _ = [
                OrderedProductItemToken(
                    item=retval,
                    serial=i,
                    seat=seat,
                    valid=True
                    )
                for i, seat in core_api.iterate_serial_and_seat(element)
                ]
            return retval

        proto_order = cls(
            order_no=order_like.order_no,
            total_amount=order_like.total_amount,
            shipping_address=order_like.shipping_address,
            payment_delivery_pair=order_like.payment_delivery_pair,
            system_fee=order_like.system_fee,
            special_fee_name=order_like.special_fee_name,
            special_fee=order_like.special_fee,
            transaction_fee=order_like.transaction_fee,
            delivery_fee=order_like.delivery_fee,
            performance=order_like.performance,
            sales_segment=order_like.sales_segment,
            organization_id=order_like.organization_id,
            operator=order_like.operator,
            user=order_like.user,
            membership=order_like.membership,
            membergroup=order_like.membergroup,
            issuing_start_at=order_like.issuing_start_at,
            issuing_end_at=order_like.issuing_end_at,
            payment_due_at=order_like.payment_due_at,
            note=note,
            attributes=attributes,
            cart_setting_id=order_like.cart_setting_id,
            user_point_accounts=order_like.user_point_accounts,
            items=[
                OrderedProduct(
                    product=item.product,
                    price=item.price,
                    quantity=item.quantity,
                    elements=[ build_element(element) for element in item.elements ]
                    )
                for item in order_like.items
                ]
            )
        return proto_order


class OrderSummary(Base):
    __mapper_args__ = dict(
        include_properties=[
            Order.__table__.c.id,
            Order.__table__.c.organization_id,
            Performance.__table__.c.event_id,
            Performance.__table__.c.start_on,
            Performance.__table__.c.end_on,
            Order.__table__.c.performance_id,
            Order.__table__.c.sales_segment_id,
            Order.__table__.c.order_no,
            Order.__table__.c.created_at,
            Order.__table__.c.paid_at,
            Order.__table__.c.delivered_at,
            Order.__table__.c.canceled_at,
            Order.__table__.c.refund_id,
            Order.__table__.c.refunded_at,
            Order.__table__.c.transaction_fee,
            Order.__table__.c.delivery_fee,
            Order.__table__.c.system_fee,
            Order.__table__.c.special_fee,
            Order.__table__.c.special_fee_name,
            Order.__table__.c.total_amount,
            Order.__table__.c.refund_transaction_fee,
            Order.__table__.c.refund_delivery_fee,
            Order.__table__.c.refund_system_fee,
            Order.__table__.c.refund_special_fee,
            Order.__table__.c.refund_total_amount,
            Order.__table__.c.note,
            Order.__table__.c.payment_delivery_method_pair_id,
            Order.__table__.c.shipping_address_id,
            Order.__table__.c.issued,
            Order.__table__.c.user_id,
            Order.__table__.c.refund_id,
            Order.__table__.c.fraud_suspect,
            Order.__table__.c.cart_setting_id,
            Order.__table__.c.created_at,
            Order.__table__.c.deleted_at,
            UserProfile.__table__.c.last_name.label('user_profile_last_name'),
            UserProfile.__table__.c.first_name.label('user_profile_first_name'),
            UserProfile.__table__.c.last_name_kana.label('user_profile_last_name_kana'),
            UserProfile.__table__.c.first_name_kana.label('user_profile_first_name_kana'),
            UserProfile.__table__.c.nick_name.label('user_profile_nick_name'),
            UserProfile.__table__.c.sex.label('user_profile_sex'),
            ShippingAddress.__table__.c.last_name,
            ShippingAddress.__table__.c.first_name,
            ShippingAddress.__table__.c.last_name_kana,
            ShippingAddress.__table__.c.first_name_kana,
            ShippingAddress.__table__.c.zip,
            ShippingAddress.__table__.c.country,
            ShippingAddress.__table__.c.prefecture,
            ShippingAddress.__table__.c.city,
            ShippingAddress.__table__.c.tel_1,
            ShippingAddress.__table__.c.tel_2,
            ShippingAddress.__table__.c.address_1,
            ShippingAddress.__table__.c.address_2,
            ShippingAddress.__table__.c.fax,
            ShippingAddress.__table__.c.email_1,
            ShippingAddress.__table__.c.email_2,
            PaymentMethod.__table__.c.name.label('payment_method_name'),
            PaymentMethod.__table__.c.payment_plugin_id,
            DeliveryMethod.__table__.c.name.label('delivery_method_name'),
            DeliveryMethod.__table__.c.delivery_plugin_id,
            Membership.__table__.c.name.label('membership_name'),
            Membership.__table__.c.id.label('membership_id'),
            ],
        primary_key=[
            Order.__table__.c.id
            ],
        )

    id = Order.id
    organization = orm.relationship('Organization', primaryjoin=(Order.organization_id == Organization.id))
    organization_id = Order.organization_id
    event_id = Performance.event_id
    performance_start_on = Performance.start_on
    performance_end_on = Performance.end_on
    performance_id = Order.performance_id
    sales_segment_id = Order.sales_segment_id
    order_no = Order.order_no
    created_at = Order.created_at
    paid_at = Order.paid_at
    delivered_at = Order.delivered_at
    canceled_at = Order.canceled_at
    refund_id = Order.refund_id
    refunded_at = Order.refunded_at
    transaction_fee = Order.transaction_fee
    delivery_fee = Order.delivery_fee
    system_fee = Order.system_fee
    total_amount = Order.total_amount
    refund_transaction_fee = Order.refund_transaction_fee
    refund_delivery_fee = Order.refund_delivery_fee
    refund_system_fee = Order.refund_system_fee
    refund_special_fee = Order.refund_special_fee
    refund_total_amount = Order.refund_total_amount
    note = Order.note
    payment_delivery_method_pair_id = Order.payment_delivery_method_pair_id
    shipping_address_id = Order.shipping_address_id
    issued = Order.issued
    user_id = Order.user_id
    refund_id = Order.refund_id
    fraud_suspect = Order.fraud_suspect
    created_at = Order.created_at
    deleted_at = Order.deleted_at
    user_profile_last_name = UserProfile.__table__.c.last_name
    user_profile_first_name = UserProfile.__table__.c.first_name
    user_profile_last_name_kana = UserProfile.__table__.c.last_name_kana
    user_profile_first_name_kana = UserProfile.__table__.c.first_name_kana
    user_profile_nick_name = UserProfile.__table__.c.nick_name
    user_profile_sex = UserProfile.__table__.c.sex
    last_name = ShippingAddress.last_name
    first_name = ShippingAddress.first_name
    last_name_kana = ShippingAddress.last_name_kana
    first_name_kana = ShippingAddress.first_name_kana
    zip = ShippingAddress.zip
    country = ShippingAddress.country
    prefecture = ShippingAddress.prefecture
    city = ShippingAddress.city
    tel_1 = ShippingAddress.tel_1
    tel_2 = ShippingAddress.tel_2
    address_1 = ShippingAddress.address_1
    address_2 = ShippingAddress.address_2
    fax = ShippingAddress.fax
    email_1 = ShippingAddress.email_1
    email_2 = ShippingAddress.email_2
    payment_method_id = PaymentMethod.id
    payment_method_name = PaymentMethod.__table__.c.name
    payment_plugin_id = PaymentMethod.__table__.c.payment_plugin_id
    delivery_method_id = DeliveryMethod.id
    delivery_method_name = DeliveryMethod.__table__.c.name
    delivery_plugin_id = DeliveryMethod.__table__.c.delivery_plugin_id
    membership_id = Membership.__table__.c.id
    membership_name = Membership.__table__.c.name
    membergroup_id = MemberGroup.__table__.c.id
    membergroup_name = MemberGroup.__table__.c.name
    cart_setting_id = Order.cart_setting_id

    __table__ = Order.__table__ \
        .join(
            PaymentDeliveryMethodPair.__table__,
            and_(Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id,
                 PaymentDeliveryMethodPair.deleted_at==None)
            ) \
        .join(
            PaymentMethod.__table__,
            and_(PaymentDeliveryMethodPair.payment_method_id==PaymentMethod.id,
                 PaymentMethod.deleted_at==None)
            ) \
        .join(
            DeliveryMethod.__table__,
            and_(PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id,
                 DeliveryMethod.deleted_at==None)
            ) \
        .join(
            Performance.__table__,
            and_(Performance.id==Order.performance_id,
                 Performance.deleted_at==None)
            ) \
        .outerjoin(
            ShippingAddress.__table__,
            and_(Order.shipping_address_id==ShippingAddress.id,
                 ShippingAddress.deleted_at==None)
            ) \
        .outerjoin(
            User.__table__,
            and_(Order.user_id==User.id,
                 User.deleted_at==None)
            ) \
        .outerjoin(
            UserProfile.__table__,
            and_(User.id==UserProfile.user_id,
                 UserProfile.deleted_at==None)
            ) \
        .outerjoin(
            Membership.__table__,
            and_(Order.membership_id==Membership.id,
                 Membership.deleted_at==None)
            ) \
        .outerjoin(
            MemberGroup.__table__,
            and_(Order.membergroup_id==MemberGroup.id,
                 MemberGroup.deleted_at==None)
            )

    @property
    def ordered_products(self):
        return self.items

    _attributes = orm.relationship('OrderAttribute', primaryjoin=Order.id==OrderAttribute.order_id, lazy=False)
    @property
    def attributes(self):
        return dict((a.name, a.value) for a in self._attributes)

    items = orm.relationship('OrderedProduct', primaryjoin=Order.id==OrderedProduct.order_id)
    refund = orm.relationship('Refund', primaryjoin=Order.refund_id==Refund.id, lazy=False)
    created_from_lot_entry = orm.relationship('LotEntry', foreign_keys=[Order.order_no], primaryjoin=and_(LotEntry.entry_no==Order.order_no, LotEntry.deleted_at==None), uselist=False)
    sales_segment = orm.relationship('SalesSegment', primaryjoin=(Order.sales_segment_id == SalesSegment.id), lazy=False)

    def cart_setting_primary_join():
        from altair.app.ticketing.cart.models import CartSetting
        return Order.cart_setting_id == CartSetting.id

    cart_setting = orm.relationship('CartSetting', primaryjoin=cart_setting_primary_join)

    @property
    def status(self):
        if self.canceled_at:
            return 'canceled'
        elif self.delivered_at:
            return 'delivered'
        else:
            return 'ordered'

    @property
    def payment_status(self):
        if self.refund_id and not self.refunded_at:
            return 'refunding'
        elif self.refunded_at:
            return 'refunded'
        elif self.paid_at:
            return 'paid'
        else:
            return 'unpaid'

    @property
    def user(self):
        return SummarizedUser(
            session_partaken_by(self),
            self.user_id,
            self.membership_id,
            self.membergroup_id,
            SummarizedUserProfile(
                self.user_profile_last_name,
                self.user_profile_first_name,
                self.user_profile_last_name_kana,
                self.user_profile_first_name_kana,
                self.user_profile_nick_name,
                self.user_profile_sex
                )
            )

    @reify
    def sej_order(self):
        return sej_api.get_sej_order(self.order_no)

    @reify
    def multicheckout_info(self):
        from .api import get_multicheckout_info
        return get_multicheckout_info(self.request, self)

    @property
    def card_brand(self):
        return self.multicheckout_info and self.multicheckout_info['card_brand']

    @property
    def card_ahead_com_code(self):
        return self.multicheckout_info and self.multicheckout_info['ahead_com_cd']

    @property
    def card_ahead_com_name(self):
        return self.multicheckout_info and self.multicheckout_info['ahead_com_name']

    @property
    def multicheckout_approval_no(self):
        return self.multicheckout_info and self.multicheckout_info['approval_no']

    def _shipping_address(self):
        if self.shipping_address_id is None:
            return None

        return SummarizedShippingAddress(
            self.last_name,
            self.first_name,
            self.last_name_kana,
            self.first_name_kana,
            self.zip,
            self.country,
            self.prefecture,
            self.city,
            self.address_1,
            self.address_2,
            self.tel_1,
            self.tel_2,
            self.fax,
            self.email_1,
            self.email_2,
        )
    rel_shipping_address = orm.relationship("ShippingAddress", primaryjoin=Order.shipping_address_id==ShippingAddress.id)
    shipping_address = HybridRelation(_shipping_address, rel_shipping_address)

    def _payment_delivery_pair(self):
        return SummarizedPaymentDeliveryMethodPair(
            SummarizedPaymentMethod(self.payment_plugin_id, self.payment_method_name),
            SummarizedDeliveryMethod(self.delivery_plugin_id, self.delivery_method_name))

    rel_payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair", primaryjoin=Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id)
    payment_delivery_pair = HybridRelation(_payment_delivery_pair, rel_payment_delivery_pair)

    def _performance(self):
        return _get_performance(self.request, self.performance_id, self.organization_id)

    rel_performance = orm.relationship("Performance")
    performance = HybridRelation(_performance, rel_performance)

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None

    @reify
    def membership(self):
        return SummarizedMembership(self.membership_name)

    @reify
    def membergroup(self):
        return SummarizedMemberGroup(self.membergroup_name)

    def _init_on_load(self, context):
        self.request = context.query._request

sqlalchemy.event.listen(OrderSummary, 'load', OrderSummary._init_on_load)
