# encoding: utf-8
import logging
import itertools
from datetime import datetime, timedelta
import sqlalchemy as sa
import sqlalchemy.orm.collections 
import sqlalchemy.orm as orm
from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import exists, desc, select, case
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from pyramid.threadlocal import get_current_request
from zope.interface import implementer
from zope.deprecation import deprecation

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
)
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    Member,
    Membership,
    UserCredential,
)
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.sej.exceptions import SejError
from altair.app.ticketing.sej import userside_api
from altair.app.ticketing.models import (
    Base,
)
from altair.app.ticketing.core import api as core_api

logger = logging.getLogger(__name__)


class SummarizedUser(object):
    def __init__(self, session, id, user_profile, user_credential):
        self.session = session
        self.id = id
        self.user_profile = user_profile
        self.user_credential = [user_credential]
        self.first_user_credential = user_credential

    @property
    def member(self):
        return self.session.query(Member).filter_by(user_id=self.id).first()

class SummarizedUserCredential(object):
    def __init__(self, auth_identifier, membership):
        self.auth_identifier = auth_identifier
        self.membership = membership

class SummarizedMembership(object):
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
    def __init__(self, name):
        self.name = name

class SummarizedDeliveryMethod(object):
    def __init__(self, name):
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

@implementer(IOrderLike)
class Order(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Order'
    __table_args__= (
        sa.UniqueConstraint('order_no', 'branch_no', name="ix_Order_order_no_branch_no"),
        )
    __clone_excluded__ = ['cart', 'ordered_from', 'payment_delivery_pair', 'performance', 'user', '_attributes', 'refund', 'operator', 'lot_entries', 'lot_wishes', 'point_grant_history_entries', 'sales_segment']

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

    special_fee_name = sa.Column(sa.Unicode(255), nullable=False, default=u"")
    special_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False, default=0)

    transaction_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)

    multicheckout_approval_no = sa.Column(sa.Unicode(255), doc=u"マルチ決済受領番号")

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

    card_brand = sa.Column(sa.Unicode(20))
    card_ahead_com_code = sa.Column(sa.Unicode(20), doc=u"仕向け先企業コード")
    card_ahead_com_name = sa.Column(sa.Unicode(20), doc=u"仕向け先企業名")

    fraud_suspect = sa.Column(sa.Boolean, nullable=True, default=None)
    browserid = sa.Column(sa.Unicode(40))

    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref='orders')

    issuing_start_at = sa.Column(sa.DateTime, nullable=True)
    issuing_end_at   = sa.Column(sa.DateTime, nullable=True)
    payment_start_at = sa.Column(sa.DateTime, nullable=True)
    payment_due_at   = sa.Column(sa.DateTime, nullable=True)

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
    def sej_order(self):
        return sej_api.get_sej_order(self.order_no)

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
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None

    @property
    def prev(self):
        from altair.app.ticketing.models import DBSession
        return DBSession.query(Order, include_deleted=True).filter_by(order_no=self.order_no).filter_by(branch_no=self.branch_no-1).one()

    @property
    def checkout(self):
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.checkout.models import Checkout
        return Cart.query.filter(Cart._order_no==self.order_no).join(Checkout).with_entities(Checkout).first()

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

    def cancel(self, request, payment_method=None, now=None):
        now = now or datetime.now()
        if not self.can_refund() and not self.can_cancel():
            logger.info('order (%s) cannot cancel status (%s, %s)' % (self.id, self.status, self.payment_status))
            return False

        '''
        決済方法ごとに払戻処理
        '''
        if payment_method:
            ppid = payment_method.payment_plugin_id
        else:
            ppid = self.payment_delivery_pair.payment_method.payment_plugin_id
        if not ppid:
            return False

        tenant = userside_api.lookup_sej_tenant(request, self.organization_id)

        # インナー予約の場合はAPI決済していないのでスキップ
        # ただしコンビニ決済はインナー予約でもAPIで通知しているので処理する
        if self.is_inner_channel and ppid != plugins.SEJ_PAYMENT_PLUGIN_ID:
            logger.info(u'インナー予約のキャンセルなので決済払戻処理をスキップ %s' % self.order_no)

        # クレジットカード決済
        elif ppid == plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID:
            # 入金済みなら決済をキャンセル
            if self.payment_status in ['paid', 'refunding']:
                # 売り上げキャンセル
                from altair.multicheckout.api import get_multicheckout_3d_api
                organization = Organization.get(self.organization_id)
                multicheckout_api = get_multicheckout_3d_api(request, organization.setting.multicheckout_shop_name)

                order_no = self.order_no
                if request.registry.settings.get('multicheckout.testing', False):
                    order_no = self.order_no + "00"

                # キャンセルAPIでなく売上一部取消APIを使う
                # - 払戻期限を越えてもキャンセルできる為
                # - 売上一部取消で減額したあと、キャンセルAPIをつかうことはできない為
                # - ただし、売上一部取消APIを有効にする以前に予約があったものはキャンセルAPIをつかう
                if self.payment_status in ['refunding']:
                    logger.info(u'売上一部取消APIで払戻 %s' % self.order_no)
                    prev = self.prev
                    total_amount = prev.refund.item(prev) + prev.refund.fee(prev)
                    multi_checkout_result = multicheckout_api.checkout_sales_part_cancel(order_no, total_amount, 0)
                else:
                    sales_part_cancel_enabled_from = '2012-12-03 08:00'
                    if self.created_at < datetime.strptime(sales_part_cancel_enabled_from, "%Y-%m-%d %H:%M"):
                        logger.info(u'キャンセルAPIでキャンセル %s' % self.order_no)
                        multi_checkout_result = multicheckout_api.checkout_sales_cancel(order_no)
                    else:
                        logger.info(u'売上一部取消APIで全額取消 %s' % self.order_no)
                        multi_checkout_result = multicheckout_api.checkout_sales_part_cancel(order_no, self.total_amount, 0)

                error_code = ''
                if multi_checkout_result.CmnErrorCd and multi_checkout_result.CmnErrorCd != '000000':
                    error_code = multi_checkout_result.CmnErrorCd
                elif multi_checkout_result.CardErrorCd and multi_checkout_result.CardErrorCd != '000000':
                    error_code = multi_checkout_result.CardErrorCd

                if error_code:
                    logger.error(u'クレジットカード決済のキャンセルに失敗しました。 %s' % error_code)
                    return False

                self.multi_checkout_approval_no = multi_checkout_result.ApprovalNo

        # 楽天あんしん支払いサービス
        elif ppid == plugins.CHECKOUT_PAYMENT_PLUGIN_ID:
            # 入金済みなら決済をキャンセル
            if self.payment_status in ['paid', 'refunding']:
                from altair.app.ticketing.checkout import api as checkout_api
                from altair.app.ticketing.core import api as core_api
                service = checkout_api.get_checkout_service(request, self.ordered_from, core_api.get_channel(self.channel))
                checkout = self.checkout
                if self.payment_status == 'refunding':
                    # 払戻(合計100円以上なら注文金額変更API、0円なら注文キャンセルAPIを使う)
                    if self.total_amount >= 100:
                        result = service.request_change_order([checkout.orderControlId])
                        # オーソリ済みになるので売上バッチの処理対象になるようにsales_atをクリア
                        checkout.sales_at = None
                        checkout.save()
                    elif self.total_amount == 0:
                        result = service.request_cancel_order([checkout.orderControlId])
                    else:
                        logger.error(u'0円以上100円未満の注文は払戻できません (order_no=%s)' % self.order_no)
                        return False
                    if 'statusCode' in result and result['statusCode'] != '0':
                        logger.error(u'あんしん決済を払戻できませんでした %s' % result)
                        return False
                else:
                    # 売り上げキャンセル
                    logger.debug(u'売り上げキャンセル')
                    result = service.request_cancel_order([checkout.orderControlId])
                    if 'statusCode' in result and result['statusCode'] != '0':
                        logger.error(u'あんしん決済をキャンセルできませんでした %s' % result)
                        return False

        # コンビニ決済 (セブン-イレブン)
        elif ppid == plugins.SEJ_PAYMENT_PLUGIN_ID:
            sej_order = self.sej_order

            # 未入金ならコンビニ決済のキャンセル通知
            if self.payment_status == 'unpaid':
                try:
                    sej_api.cancel_sej_order(request, tenant=tenant, sej_order=sej_order, now=now)
                except SejError:
                    logger.exception(u'cancel could not be processed')
                    return False

            # 入金済み、払戻予約ならコンビニ決済の払戻通知
            elif self.payment_status in ['paid', 'refunding']:
                from altair.app.ticketing.orders.api import (
                    get_refund_per_order_fee,
                    get_refund_per_ticket_fee,
                    get_refund_ticket_price,
                    )
                try:
                    sej_api.refund_sej_order(
                        request,
                        tenant=tenant,
                        sej_order=sej_order,
                        performance_name=self.performance.name,
                        performance_code=self.performance.code,
                        performance_start_on=self.performance.start_on,
                        per_order_fee=get_refund_per_order_fee(
                            self.prev.refund,
                            self.prev
                            ),
                        per_ticket_fee=get_refund_per_ticket_fee(
                            self.prev.refund,
                            self.prev
                            ),
                        refund_start_at=self.refund.start_at,
                        refund_end_at=self.refund.end_at,
                        ticket_expire_at=self.refund.end_at + timedelta(days=+7),
                        ticket_price_getter=lambda sej_ticket: \
                            get_refund_ticket_price(
                                self.prev.refund,
                                self.prev,
                                sej_ticket.product_item_id
                                ),
                        now=now
                        )
                except SejError:
                    logger.exception(u'refund could not be processed')
                    return False

        # 窓口支払
        elif ppid == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID:
            pass

        '''
        配送方法ごとに取消処理
        '''
        # コンビニ受取
        dpid = self.payment_delivery_pair.delivery_method.delivery_plugin_id
        if dpid == plugins.SEJ_DELIVERY_PLUGIN_ID and ppid != plugins.SEJ_PAYMENT_PLUGIN_ID:
            sej_order = self.sej_order
            # SejAPIでエラーのケースではSejOrderはつくられないのでスキップ
            if sej_order:
                try:
                    sej_api.cancel_sej_order(request, tenant=tenant, sej_order=sej_order, now=now)
                except SejError:
                    logger.exception('SejOrder (order_no=%s) cancel error' % self.order_no)
                    return False
            else:
                logger.info('skip cancel delivery method. SejOrder not found (order_no=%s)' % self.order_no)

        # 在庫を戻す
        logger.info('try release stock (order_no=%s)' % self.order_no)
        self.release()
        if self.payment_status != 'refunding':
            self.mark_canceled()
        if self.payment_status in ['paid', 'refunding']:
            self.mark_refunded()

        self.save()
        logger.info('success order cancel (order_no=%s)' % self.order_no)

        return True

    def mark_canceled(self, now=None):
        self.canceled_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_refunded(self, now=None):
        self.refunded_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_delivered(self, now=None):
        self.delivered_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_paid(self, now=None):
        self.paid_at = now or datetime.now()

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

    @staticmethod
    def reserve_refund(kwargs):
        refund = Refund(**kwargs)
        refund.save()

    def call_refund(self, request):
        # 払戻対象の金額をクリア
        order = Order.clone(self, deep=True)
        if self.refund.include_system_fee:
            order.system_fee = 0
        if self.refund.include_special_fee:
            order.special_fee = 0
        if self.refund.include_transaction_fee:
            order.transaction_fee = 0
        if self.refund.include_delivery_fee:
            order.delivery_fee = 0
        if self.refund.include_item:
            for ordered_product in order.items:
                ordered_product.price = 0
                for ordered_product_item in ordered_product.ordered_product_items:
                    ordered_product_item.price = 0
        fee = order.special_fee + order.system_fee + order.transaction_fee + order.delivery_fee
        order.total_amount = sum(o.price * o.quantity for o in order.items) + fee

        try:
            return order.cancel(request, self.refund.payment_method)
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
            user=cart.shipping_address and cart.shipping_address.user,
            issuing_start_at=cart.issuing_start_at,
            issuing_end_at=cart.issuing_end_at,
            payment_start_at=cart.payment_start_at,
            payment_due_at=cart.payment_due_at
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


@implementer(IOrderedProductItemLike)
class OrderedProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProductItem'
    __clone_excluded__ = ['ordered_product_id', 'product_item', 'seats', '_attributes']

    id = sa.Column(Identifier, primary_key=True)
    ordered_product_id = sa.Column(Identifier, sa.ForeignKey("OrderedProduct.id"))
    ordered_product = orm.relationship('OrderedProduct', backref='elements')
    product_item_id = sa.Column(Identifier, sa.ForeignKey("ProductItem.id"))
    product_item = orm.relationship('ProductItem', backref='ordered_product_items')
    issued_at = sa.Column(sa.DateTime, nullable=True, default=None)
    printed_at = sa.Column(sa.DateTime, nullable=True, default=None)
    seats = orm.relationship("Seat", secondary=orders_seat_table, backref='ordered_product_items')
    price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)

    _attributes = orm.relationship("OrderedProductAttribute", backref='ordered_product_item', collection_class=orm.collections.attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderedProductAttribute(name=k, value=v))

    # 実際の購入数
    quantity = sa.Column(sa.Integer, nullable=False, default=1, server_default='1')

    @property
    def seat_statuses_for_update(self):
        from altair.app.ticketing.models import DBSession
        if len(self.seats) > 0:
            return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).with_lockmode('update').all()
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
    status = sa.Column(sa.Integer, nullable=False)
    count = sa.Column(sa.Integer, nullable=False)
    data = sa.Column(sa.UnicodeText(8388608))
    errors = sa.Column(MutationDict.as_mutable(JSONEncodedDict(65536)), nullable=True)

    organization = orm.relationship('Organization')
    performance = orm.relationship('Performance')
    operator = orm.relationship('Operator')

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
    order_import_task = orm.relationship('OrderImportTask', backref='proto_orders')

    new_order_created_at = sa.Column(sa.TIMESTAMP, nullable=True, default=None)
    new_order_paid_at = sa.Column(sa.DateTime, nullable=True, default=None)

    def mark_processed(self, now=None):
        self.processed_at = now or datetime.now()

    @classmethod
    def create_from_order_like(cls, order_like):
        note = getattr(order_like, 'note', None)
        attributes = dict(getattr(order_like, 'attributes', {}))
        proto_order_like = cls(
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
            user=order_like.shipping_address and order_like.shipping_address.user,
            issuing_start_at=order_like.issuing_start_at,
            issuing_end_at=order_like.issuing_end_at,
            payment_due_at=order_like.payment_due_at,
            note=note,
            attributes=attributes,
            items=[
                OrderedProduct(
                    product=item.product,
                    price=item.price,
                    quantity=item.quantity,
                    elements=[
                        OrderedProductItem(
                            product_item=element.product_item,
                            price=element.price,
                            quantity=element.product_item.quantity * item.quantity,
                            seats=element.seats,
                            tokens=[
                                OrderedProductItemToken(
                                    serial=i,
                                    seat=seat,
                                    valid=True
                                    )
                                for i, seat in core_api.iterate_serial_and_seat(element)
                                ]
                            )
                        for element in item.elements
                        ]
                    )
                for item in order_like.items
                ]
            )
        return proto_order_like


class OrderSummary(Base):
    __mapper_args__ = dict(
        include_properties=[
            Order.__table__.c.id,
            Order.__table__.c.organization_id,
            Performance.__table__.c.event_id,
            Performance.__table__.c.start_on,
            Performance.__table__.c.end_on,
            Order.__table__.c.performance_id,
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
            Order.__table__.c.note,
            Order.__table__.c.card_brand,
            Order.__table__.c.card_ahead_com_code,
            Order.__table__.c.card_ahead_com_name,
            Order.__table__.c.payment_delivery_method_pair_id,
            Order.__table__.c.shipping_address_id,
            Order.__table__.c.issued,
            Order.__table__.c.user_id,
            Order.__table__.c.fraud_suspect,
            Order.__table__.c.created_at,
            Order.__table__.c.deleted_at,
            UserProfile.__table__.c.last_name.label('user_profile_last_name'),
            UserProfile.__table__.c.first_name.label('user_profile_first_name'),
            UserProfile.__table__.c.last_name_kana.label('user_profile_last_name_kana'),
            UserProfile.__table__.c.first_name_kana.label('user_profile_first_name_kana'),
            UserProfile.__table__.c.nick_name.label('user_profile_nick_name'),
            UserProfile.__table__.c.sex.label('user_profile_sex'),
            UserCredential.__table__.c.auth_identifier,
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
            DeliveryMethod.__table__.c.name.label('delivery_method_name'),
            Membership.__table__.c.name.label('membership_name'),
            ],
        primary_key=[
            Order.__table__.c.id
            ],
        )

    id = Order.id
    organization_id = Order.organization_id
    event_id = Performance.event_id
    performance_start_on = Performance.start_on
    performance_end_on = Performance.end_on
    performance_id = Order.performance_id
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
    note = Order.note
    card_brand = Order.card_brand
    card_ahead_com_code = Order.card_ahead_com_code
    card_ahead_com_name = Order.card_ahead_com_name
    payment_delivery_method_pair_id = Order.payment_delivery_method_pair_id
    shipping_address_id = Order.shipping_address_id
    issued = Order.issued
    user_id = Order.user_id
    fraud_suspect = Order.fraud_suspect
    created_at = Order.created_at
    deleted_at = Order.deleted_at
    user_profile_last_name = UserProfile.__table__.c.last_name
    user_profile_first_name = UserProfile.__table__.c.first_name
    user_profile_last_name_kana = UserProfile.__table__.c.last_name_kana
    user_profile_first_name_kana = UserProfile.__table__.c.first_name_kana
    user_profile_nick_name = UserProfile.__table__.c.nick_name
    user_profile_sex = UserProfile.__table__.c.sex
    auth_identifier = UserCredential.auth_identifier
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
    delivery_method_id = DeliveryMethod.id
    delivery_method_name = DeliveryMethod.__table__.c.name
    membership_name = Membership.__table__.c.name

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
            UserCredential.__table__,
            and_(User.id==UserCredential.user_id,
                 UserCredential.deleted_at==None)
            ) \
        .outerjoin(
            Membership.__table__,
            and_(UserCredential.membership_id==Membership.id,
                 Membership.deleted_at==None)
            )

    ordered_products = orm.relationship('OrderedProduct', primaryjoin=Order.id==OrderedProduct.order_id)
    items = orm.relationship('OrderedProduct', primaryjoin=Order.id==OrderedProduct.order_id)
    refund = orm.relationship('Refund', primaryjoin=Order.refund_id==Refund.id)
    created_from_lot_entry = orm.relationship('LotEntry', foreign_keys=[Order.order_no], primaryjoin=and_(LotEntry.entry_no==Order.order_no, LotEntry.deleted_at==None), uselist=False)

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
            SummarizedUserProfile(
                self.user_profile_last_name,
                self.user_profile_first_name,
                self.user_profile_last_name_kana,
                self.user_profile_first_name_kana,
                self.user_profile_nick_name,
                self.user_profile_sex
                ),
            SummarizedUserCredential(
                self.auth_identifier,
                SummarizedMembership(
                    self.membership_name
                    )
                )
            )

    @property
    def sej_order(self):
        return sej_api.get_sej_order(self.order_no)

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
            SummarizedPaymentMethod(self.payment_method_name),
            SummarizedDeliveryMethod(self.delivery_method_name))

    rel_payment_delivery_pair = orm.relationship("PaymentDeliveryMethodPair", primaryjoin=Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id)
    payment_delivery_pair = HybridRelation(_payment_delivery_pair, rel_payment_delivery_pair)

    def _performance(self):
        request = get_current_request()
        return _get_performance(request, self.performance_id, self.organization_id)

    rel_performance = orm.relationship("Performance")
    performance = HybridRelation(_performance, rel_performance)

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None


