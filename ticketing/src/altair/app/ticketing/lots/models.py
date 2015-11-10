# -*- coding:utf-8 -*-

"""
選択制限をオプショナルでかけられる

公演を排他的
    たとえば第一希望と第二希望などで、同じ公演を選択できない

席種を排他
    たとえば第一希望と第二希望などで、 **公演に関係なく** 同じ席種を選択できない

公演・席種を排他
    たとえば第一希望と第二希望などで、 **同じ公演の** 同じ席種を選択できない

"""
from datetime import datetime, timedelta
import logging

import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.associationproxy import association_proxy
from altair.app.ticketing.core.interfaces import IPurchase
from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.exc import NoResultFound
from zope.deprecation import deprecate
from zope.interface import implementer

logger = logging.getLogger(__name__)

from altair.app.ticketing.utils import StandardEnum
from altair.app.ticketing.models import (
    Identifier,
    Base,
    BaseModel,
    WithTimestamp,
    LogicallyDeleted,
    DBSession,
)

from altair.app.ticketing.core.models import (
    Product,
    ProductItem,
    SalesSegment,
    )

from altair.app.ticketing.users.models import (
    SexEnum,
)
from altair.app.ticketing.cart.models import (
    Cart,
)
from .events import LotClosedEvent

class LotSelectionEnum(StandardEnum):
    NoCare = 0
    ExclusivePerformance = 1
    ExclusiveStockType = 2
    ExclusivePerformanceStockType = 3


class LotStatusEnum(StandardEnum):
    New = 0
    Lotting = 1
    Electing = 2 # ワークデータ取り込み済
    Elected = 3 # 確定処理実行済
    Sent = 4

class LotEntryStatusEnum(StandardEnum):
    New = 0
    Elected = 1
    Rejected = 2
    Ordered = 3
    Withdrawn = 4 #ユーザ取消

Lot_SalesSegment = sa.Table(
    "Lot_SalesSegment",
    Base.metadata,
    sa.Column("lot_id", Identifier, sa.ForeignKey("Lot.id")),
    sa.Column("sales_segment_id", Identifier, sa.ForeignKey("SalesSegment.id")),
)


class Lot(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Lot'
    __clone_excluded__ = ['status']

    id = sa.Column(Identifier, primary_key=True)
    name = sa.Column(sa.String(255))

    limit_wishes = sa.Column(sa.Integer, doc=u"希望数")

    event_id = sa.Column(Identifier, sa.ForeignKey('Event.id'))
    event = orm.relationship('Event', backref='lots')

    selection_type = sa.Column(sa.Integer) # LotSelectionEnum

    # sales_segment_group_id = sa.Column(Identifier, sa.ForeignKey('SalesSegmentGroup.id'))
    # sales_segment_group = orm.relationship('SalesSegmentGroup', backref="lots")
    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref="lots")

    status = sa.Column(sa.Integer, default=int(LotStatusEnum.New))

    description = sa.Column(sa.UnicodeText)
    entry_limit = sa.Column(sa.Integer, default=0, server_default="0")

    lotting_announce_datetime = sa.Column(sa.DateTime, doc=u"抽選結果発表予定日")
    lotting_announce_timezone = sa.Column(sa.String(255))
    custom_timezone_label = sa.Column(sa.String(255))

    system_fee = sa.Column(sa.Numeric(precision=16, scale=2), default=0,
                           server_default="0")

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='lots')

    mail_send_now = sa.Column('mail_send_now', sa.Boolean(), nullable=False, default=False)

    @staticmethod
    def create_from_template(template, **kwds):
        obj = Lot.clone(template)
        if 'event_id' in kwds:
            obj.event_id = kwds['event_id']
        if 'sales_segment_id' in kwds:
            obj.sales_segment_id = kwds['sales_segment_id']
        obj.save()
        return obj

    @property
    def electing_works(self):
        return LotElectWork.query.filter(
            LotElectWork.lot_id==self.id
        ).filter(
            LotEntry.entry_no==LotElectWork.lot_entry_no
        ).filter(
            sql.and_(LotEntry.elected_at==None,
                     LotEntry.ordered_mail_sent_at==None)
        ).all()

    auth_type = sa.Column(sa.Unicode(255))

    @property
    def remained_entries(self):
        """ 当選以外のエントリ"""

        return LotEntry.query.filter(
            LotEntry.elected_at==None
        ).filter(
            LotEntry.order_id==None
        ).filter(
            sql.or_(LotEntry.rejected_at!=None,
                    LotEntry.canceled_at!=None,
                    LotEntry.withdrawn_at!=None)
        ).filter(
            LotEntry.lot_id==self.id
        ).all()

    @property
    def rejectable_entries(self):
        """ 落選予定指定可能なエントリ

        - 当選していない elected_at
        - まだ落選していない rejected_at
        - 当選予定でない LotElectWork
        - まだ落選予定でない LotRejectWork
        - キャンセルされてない canceled_at
        - ユーザ取消されてない withdrawn_at

        """


        return LotEntry.query.outerjoin(
            LotElectWork,
            sql.and_(LotElectWork.lot_id==self.id,
                     LotElectWork.lot_entry_no==LotEntry.entry_no),
        ).outerjoin(
            LotRejectWork,
            sql.and_(LotRejectWork.lot_id==self.id,
                     LotRejectWork.lot_entry_no==LotEntry.entry_no),
        ).filter(
            LotEntry.elected_at==None,
            LotEntry.rejected_at==None,
            LotEntry.canceled_at==None,
            LotEntry.withdrawn_at==None,
            LotEntry.lot_id==self.id,
            LotEntry.entry_no!=None,
            LotElectWork.id==None,
            LotRejectWork.id==None
        ).all()


    @property
    def query_receipt_entries(self):
        """ 申込状態のエントリ """

        return LotEntry.query.filter(
            LotEntry.lot_id==self.id
        ).filter(
            LotEntry.entry_no!=None,
        ).filter(
            LotEntry.order_id==None, # 当選していない
            LotEntry.elected_at==None, # 当選していない
            LotEntry.rejected_at==None, # 落選していない
            LotEntry.canceled_at==None, # キャンセルされていない
            LotEntry.withdrawn_at==None, #ユーザ取消されていない
        )

    @property
    def query_not_sent_mail_entries(self):
        """ メール未送信のエントリ """

        return LotEntry.query.filter(
            LotEntry.lot_id==self.id
        ).filter(
            LotEntry.entry_no!=None,
        ).filter(
            LotEntry.ordered_mail_sent_at==None, # メール未送信
            LotEntry.canceled_at==None, # キャンセルされていない
            LotEntry.withdrawn_at==None, #ユーザ取消されていない
        )

    def is_elected(self):
        return self.status == int(LotStatusEnum.Elected)

    def finish_lotting(self):
        self.status = int(LotStatusEnum.Elected)

    def start_lotting(self):
        logger.info("start lotting lot id={lot.id}".format(lot=self))
        self.status = int(LotStatusEnum.Lotting)


    def start_electing(self):
        logger.info("start electing lot id={lot.id}".format(lot=self))
        self.status = int(LotStatusEnum.Electing)

    @hybrid_method
    def is_finished(self):
        return self.status == int(LotStatusEnum.Elected)

    def elect_wishes(self, entry_wishes):
        """ 当選予定申込希望 """
        affected = 0
        for entry_no, wish_order in entry_wishes:
            wish = LotEntryWish.query.join(LotEntry).filter(
                LotEntry.lot_id==self.id,
                LotEntry.entry_no==entry_no,
                LotEntryWish.wish_order==wish_order
                ).first()
            if wish is None:
                logger.debug("not found {entry_no}, {wish_order}".format(entry_no=entry_no, wish_order=wish_order))
                continue
            # すでに当落確定 or キャンセル済み
            entry = wish.lot_entry
            if entry.is_elected or entry.is_rejected or entry.is_canceled:
                logger.debug("already elected, rejected or canceled {entry_no}".format(entry_no=entry_no))
                continue
            # すでに当選予定
            if wish.is_electing():
                logger.debug("already marked as elected {entry_no}".format(entry_no=entry_no))
                continue
            #すでにユーザ取消
            if wish.is_withdrawn():
                logger.debug("{entry_no} already withdrawn by user".format(entry_no=entry_no))
                continue
            # すでに他の希望が当選予定
            if LotElectWork.query.filter_by(lot_id=self.id, lot_entry_no=entry_no).count():
                logger.debug("already marked as electing {entry_no}".format(entry_no=entry_no))
                for w in entry.wishes:
                    for elect_work in w.works:
                        DBSession.delete(elect_work)
                        DBSession.flush()
            # すでに落選予定
            if wish.is_rejecting():
                logger.debug("already marked as rejecting {entry_no}".format(entry_no=entry_no))
                for reject_work in wish.reject_works:
                    DBSession.delete(reject_work)
                    DBSession.flush()

            w = LotElectWork(lot_id=self.id, lot_entry_no=entry_no, wish_order=wish_order,
                             entry_wish_no="{0}-{1}".format(entry_no, wish_order))
            DBSession.add(w)
            affected += 1
        return affected

    def reject_entries(self, entries):
        """ 落選予定 """
        affected = 0
        for entry_no in entries:
            entry = LotEntry.query.filter(LotEntry.lot_id==self.id, LotEntry.entry_no==entry_no).first()
            if entry is None:
                logger.debug("not found {entry_no}".format(entry_no=entry_no))
                continue
            # すでに当落確定 or キャンセル済み
            if entry.is_elected or entry.is_rejected or entry.is_canceled:
                logger.debug("already elected, rejected or canceled {entry_no}".format(entry_no=entry_no))
                continue
            # すでに落選予定
            if entry.is_rejecting():
                logger.debug("already marked as rejected {entry_no}".format(entry_no=entry_no))
                continue
            #すでにユーザ取消
            if entry.is_withdrawn:
                logger.debug("{entry_no} already withdrawn by user".format(entry_no=entry_no))
                continue
            # すでに当選予定
            if LotElectWork.query.filter_by(lot_id=self.id, lot_entry_no=entry_no).count():
                logger.debug("already marked as elected {entry_no}".format(entry_no=entry_no))
                for wish in entry.wishes:
                    for elect_work in wish.works:
                        DBSession.delete(elect_work)
                        DBSession.flush()

            w = LotRejectWork(lot_id=self.id, lot_entry_no=entry_no)
            DBSession.add(w)
            affected += 1
        return affected

    def reset_entries(self, entries):
        """ 申込に戻す """
        affected = 0
        for entry_no in entries:
            entry = LotEntry.query.filter(LotEntry.lot_id==self.id, LotEntry.entry_no==entry_no).first()
            if entry is None:
                logger.debug("not found {entry_no}".format(entry_no=entry_no))
                continue
            # すでに当落確定 or キャンセル済み
            if entry.is_elected or entry.is_rejected or entry.is_canceled:
                logger.debug("already elected, rejected or canceled {entry_no}".format(entry_no=entry_no))
                continue
            # すでに当選予定
            if LotElectWork.query.filter_by(lot_id=self.id, lot_entry_no=entry_no).count():
                logger.debug("already marked as elected {entry_no}".format(entry_no=entry_no))
                for wish in entry.wishes:
                    for elect_work in wish.works:
                        DBSession.delete(elect_work)
                        DBSession.flush()
            # すでに落選予定
            if entry.is_rejecting():
                logger.debug("already marked as rejected {entry_no}".format(entry_no=entry_no))
                for wish in entry.wishes:
                    for reject_work in wish.reject_works:
                        DBSession.delete(reject_work)
                        DBSession.flush()

            affected += 1
        return affected

    def cancel_electing(self, wish):
        LotElectWork.query.filter(
            LotElectWork.lot_id==self.id
        ).filter(
            LotElectWork.lot_entry_no==wish.lot_entry.entry_no
        ).filter(
            LotElectWork.wish_order==wish.wish_order
        ).delete()

    def cancel_rejecting(self, entry):
        LotRejectWork.query.filter(
            LotRejectWork.lot_id==self.id
        ).filter(
            LotRejectWork.lot_entry_no==entry.entry_no
        ).delete()



    def available_on(self, now):
        return ((self.start_at is None) or (self.start_at <= now)) and \
               ((self.end_at is None) or (now <= self.end_at))

    @classmethod
    def has_product(cls, product):
        return sql.and_(cls.sales_segment_id==Product.sales_segment_id,
                        Product.id==product.id)


    @property
    def products(self):
        return self.sales_segment.products

    @property
    def performances(self):
        return list(set([p.performance for p in self.products]))

    @property
    def start_at(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.start_at

    @property
    def use_default_start_at(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.use_default_start_at

    @property
    def end_at(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.end_at

    @property
    def use_default_end_at(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.use_default_end_at

    @property
    def sales_segment_group(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.sales_segment_group

    @property
    def sales_segment_group_id(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.sales_segment_group_id

    @property
    def max_quantity(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.max_quantity

    @property
    def seat_choice(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.seat_choice

    @property
    def auth3d_notice(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.auth3d_notice

    def get_elected_wishes(self):
        return DBSession.query(LotEntryWish).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotElectWork.lot_entry_no==LotEntry.entry_no
        ).filter(
            (LotElectWork.wish_order-1)==LotEntryWish.wish_order
        )

    def get_rejected_wishes(self):
        return DBSession.query(LotEntry).filter(
            LotEntry.elected_at==None
        ).filter(
            LotEntry.rejected_at==None
        ).all()

    def get_lot_entry(self, entry_no):
        return DBSession.query(LotEntry).filter(
            LotEntry.lot_id==self.id
        ).filter(
                LotEntry.entry_no==entry_no
        ).first()

    def accept_core_model_traverser(self, traverser):
        traverser.begin_lot(self)
        traverser.end_lot(self)

    def delete(self):
        self.deleted_at = datetime.now()
        if self.lot_entry_report_settings:
            for setting in self.lot_entry_report_settings:
                setting.deleted_at = self.deleted_at


lot_entry_user_point_account_table = sa.Table(
    "LotEntry_UserPointAccount", Base.metadata,
    sa.Column("lot_entry_id", Identifier, sa.ForeignKey("LotEntry.id")),
    sa.Column("user_point_account_id", Identifier, sa.ForeignKey("UserPointAccount.id"))
    )

@implementer(IPurchase)
class LotEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 抽選申し込み """

    __tablename__ = 'LotEntry'

    id = sa.Column(Identifier, primary_key=True)
    entry_no = sa.Column(sa.Unicode(20), unique=True, doc=u"抽選申し込み番号")
    channel = sa.Column(sa.Integer, nullable=True)

    # 抽選
    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship('Lot', backref='entries')

    # 申し込み情報
    shipping_address_id = sa.Column(Identifier, sa.ForeignKey('ShippingAddress.id'))
    shipping_address = orm.relationship('ShippingAddress', backref="lot_entries")

    # 申し込み時会員種別
    # membergroupだけではなくmembershipも必要なのは、"rakuten" や "nogizaka46" のように
    # membergroup を伴わない認証方式があるため
    membership_id = sa.Column(Identifier, sa.ForeignKey('Membership.id'))
    membership = orm.relationship("Membership", backref="lot_entries")
    membergroup_id = sa.Column(Identifier, sa.ForeignKey('MemberGroup.id'))
    membergroup = orm.relationship("MemberGroup", backref="lot_entries")

    elected_at = sa.Column(sa.DateTime)
    rejected_at = sa.Column(sa.DateTime)

    cart_id = sa.Column(Identifier, sa.ForeignKey(Cart.id))
    cart = orm.relationship("Cart", backref="lot_entries")

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))

    def join_cond():
        from altair.app.ticketing.orders.models import Order
        return (Order.order_no == LotEntry.entry_no) & \
               (Order.deleted_at == None)

    order = orm.relationship("Order", backref="lot_entries", foreign_keys=[entry_no], primaryjoin=join_cond)

    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey('PaymentDeliveryMethodPair.id'))
    payment_delivery_method_pair = orm.relationship('PaymentDeliveryMethodPair', backref='lot_entries')

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='lot_entries')

    _attributes = orm.relationship("LotEntryAttribute", backref='lot_entry', collection_class=orm.collections.attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: LotEntryAttribute(name=k, value=v))
    gender = sa.Column(sa.Integer, default=int(SexEnum.NoAnswer))
    birthday = sa.Column(sa.Date)
    memo = sa.Column(sa.UnicodeText)

    canceled_at = sa.Column(sa.DateTime())
    withdrawn_at = sa.Column(sa.DateTime())
    ordered_mail_sent_at = sa.Column(sa.DateTime())

    browserid = sa.Column(sa.String(40))

    closed_at = sa.Column(sa.DateTime())

    user_id = sa.Column(Identifier, sa.ForeignKey('User.id'))
    user = orm.relationship('User', backref='lot_entries')

    cart_session_id = sa.Column(sa.VARBINARY(72), unique=False)
    user_agent = sa.Column(sa.VARBINARY(200), nullable=True)

    user_point_accounts = orm.relationship('UserPointAccount', secondary=lot_entry_user_point_account_table)

    #xxx: for order
    @property
    def order_no(self):
        return self.entry_no

    @order_no.setter
    def order_no(self, value):
        self.entry_no = value

    #xxx: for order
    @property
    def payment_delivery_pair(self):
        return self.payment_delivery_method_pair

    @property
    def order_no(self):
        return self.order.order_no

    # begin [order amount fee interface]
    @property
    def total_amount(self):
        if self.order is None:
            return None
        return self.order.total_amount

    @property
    def system_fee(self):
        if self.order is None:
            return None
        return self.order.system_fee

    @property
    def special_fee(self):
        if self.order is None:
            return None
        return self.order.special_fee

    @property
    def special_fee_name(self):
        if self.order is None:
            return None
        return self.order.special_fee_name


    @property
    def transaction_fee(self):
        if self.order is None:
            return None
        return self.order.transaction_fee

    @property
    def delivery_fee(self):
        if self.order is None:
            return None
        return self.order.delivery_fee

    @property
    def sej_order(self):
        if self.order is None:
            return None
        return self.order.sej_order

    # end [order amount fee interface]

    def close(self):
        self.closed_at = datetime.now()

    def get_wish(self, wish_order):
        wish_order = int(wish_order)
        for wish in self.wishes:
            if wish.wish_order == wish_order:
                return wish

    @property
    def sales_segment(self):
        return self.lot.sales_segment

    @property
    def max_amount(self):
        """" """
        return max([w.total_amount for w in self.wishes])

    @property
    def status(self):
        retval = LotEntryStatusEnum.New
        if self.rejected_at is not None:
            retval = LotEntryStatusEnum.Rejected
        elif self.withdrawn_at is not None:
            retval = LotEntryStatusEnum.Withdrawn
        else:
            if self.elected_at is not None:
                if self.order_id is not None:
                    retval = LotEntryStatusEnum.Ordered
                else:
                    retval = LotEntryStatusEnum.Elected
        return retval

    @hybrid_property
    def is_elected(self):
        return self.elected_at != None and self.rejected_at == None

    @hybrid_property
    def is_rejected(self):
        return self.rejected_at != None

    @hybrid_property
    def is_canceled(self):
        return self.canceled_at != None

    @hybrid_property
    def is_withdrawn(self):
        return self.withdrawn_at != None

    @hybrid_property
    def is_ordered(self):
        return self.is_elected and any([w.order_id != None for w in self.wishes])

    def reject(self):
        now = datetime.now()
        self.rejected_at = now
        rejected = LotRejectedEntry(lot_entry=self)
        for wish in self.wishes:
            wish.reject(now)

        return rejected

    def elect(self, wish):
        assert wish in self.wishes
        now = datetime.now()
        self.elected_at = now
        elected = LotElectedEntry(lot_entry=self,
                                  lot_entry_wish=wish)
        for _wish in self.wishes:
            if wish == _wish:
                _wish.elect(now)
            else:
                _wish.reject(now)
        return elected

    def cancel(self):
        now = datetime.now()
        self.canceled_at = now
        for wish in self.wishes:
            wish.cancel(now)

    def withdraw(self, request):
        logger.debug("close lot entry {0} ".format(self.entry_no))
        self.close()
        event = LotClosedEvent(request, lot_entry=self)
        request.registry.notify(event)
        now = datetime.now()
        self.withdrawn_at = now
        for wish in self.wishes:
            wish.withdraw(now)

    def delete(self):
        self.deleted_at = datetime.now()

    def is_deletable(self):
        """キャンセル、取消状態の抽選申込のみ論理削除可能"""
        return self.canceled_at or self.withdrawn_at

    def is_electing(self):
        return LotElectWork.query.filter(
            LotElectWork.lot_entry_no==self.entry_no
        ).count()

    def is_rejecting(self):
        return LotRejectWork.query.filter(
            LotRejectWork.lot_entry_no==self.entry_no
        ).count()

    def get_lot_entry_attribute_pair_pairs(self, request):
        from .adapters import LotEntryCart
        from altair.app.ticketing.orders.api import get_order_attribute_pair_pairs
        order_like = LotEntryCart(self)
        return get_order_attribute_pair_pairs(request, order_like, for_='lots')

    @property
    def cart_setting(self):
        return self.lot.event.setting.cart_setting or self.lot.event.organization.setting.cart_setting


class LotEntryProductSupport(object):
    """ 表示と実モデルで利用する金額計算プロパティ """

    @property
    def subtotal(self):
        """ 購入額小計
        """
        return self.product.price * self.quantity


class LotEntryWishSupport(object):
    """ 表示と実モデルで利用する金額計算プロパティ """

    @property
    def product_quantities(self):
        """ (product, quantity) """
        return [(p.product, p.quantity)
                for p in self.products]


    @property
    def transaction_fee(self):
        """ 決済手数料 """
        return self.lot_entry.sales_segment.get_transaction_fee(self.lot_entry.payment_delivery_method_pair,
                                                                self.product_quantities)

    @property
    def delivery_fee(self):
        """ 引取手数料 """
        return self.lot_entry.sales_segment.get_delivery_fee(self.lot_entry.payment_delivery_method_pair,
                                                             self.product_quantities)

    @property
    def tickets_amount(self):
        return sum(p.subtotal for p in self.products)

    @property
    def total_amount(self):
        return self.tickets_amount + self.system_fee + self.special_fee +\
            self.transaction_fee + self.delivery_fee

    @property
    def total_quantity(self):
        return sum([p.quantity for p in self.products])

    @property
    def system_fee(self):
        #return self.lot_entry.lot.system_fee
        #return self.lot_entry.payment_delivery_method_pair.system_fee
        return self.lot_entry.sales_segment.get_system_fee(self.lot_entry.payment_delivery_method_pair,
                                                           self.product_quantities)

    @property
    def special_fee_name(self):
        return  self.lot_entry.payment_delivery_method_pair.special_fee_name

    @property
    def special_fee(self):
        return self.lot_entry.sales_segment.get_special_fee(self.lot_entry.payment_delivery_method_pair,
                                                            self.product_quantities)


class TemporaryLotEntry(object):
    def __init__(self, payment_delivery_method_pair, sales_segment):
        self.payment_delivery_method_pair = payment_delivery_method_pair
        self.sales_segment = sales_segment


class TemporaryLotEntryProduct(LotEntryProductSupport):
    def __init__(self, quantity, product):
        self.quantity = quantity
        self.product = product

class TemporaryLotEntryWish(LotEntryWishSupport):
    """ 確認画面用のオンメモリ希望内容 """

    def __init__(self, wish_order, performance,
                 payment_delivery_method_pair,
                 sales_segment):
        self.wish_order = wish_order
        self.performance = performance
        self.lot_entry = TemporaryLotEntry(payment_delivery_method_pair, sales_segment)
        self.products = []


class LotEntryWish(LotEntryWishSupport, Base, BaseModel, WithTimestamp, LogicallyDeleted):
    u""" 抽選申し込み希望 """
    __tablename__ = 'LotEntryWish'

    id = sa.Column(Identifier, primary_key=True)
    wish_order = sa.Column(sa.Integer, doc=u"希望順")
    entry_wish_no = sa.Column(sa.Unicode(30), doc=u"申し込み番号と希望順を合わせたキー項目")
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))
    performance = orm.relationship('Performance', backref="lot_entry_wishes")

    # 抽選申し込み
    lot_entry_id = sa.Column(Identifier, sa.ForeignKey('LotEntry.id'))
    lot_entry = orm.relationship('LotEntry', backref='wishes')

    elected_at = sa.Column(sa.DateTime)
    rejected_at = sa.Column(sa.DateTime)

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))
    order = orm.relationship('Order', backref='lot_wishes')

    canceled_at = sa.Column(sa.DateTime())
    withdrawn_at = sa.Column(sa.DateTime())
    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='lot_entry_wishes')


    @property
    def closed(self):
        return bool(self.lot_entry.closed_at)

    def is_electing(self):
        return LotElectWork.query.filter(
            LotElectWork.entry_wish_no==self.entry_wish_no).count()

    def is_rejecting(self):
        return LotRejectWork.query.filter(
            LotRejectWork.lot_entry_no==LotEntry.entry_no
        ).filter(
            LotEntry.id==self.lot_entry_id
        ).count()

    def is_withdrawn(self):
        return LotEntry.query.filter(
            LotEntry.id==self.lot_entry_id
        ).filter(
            LotEntry.withdrawn_at!=None
        ).count()

    @property
    def works(self):
        return LotElectWork.query.filter(
            LotElectWork.entry_wish_no==self.entry_wish_no,
        ).all()

    @property
    def reject_works(self):
        return LotRejectWork.query.filter(
            LotRejectWork.lot_entry_no==LotEntry.entry_no
        ).filter(
            LotEntry.id==self.lot_entry_id
        ).all()

    @property
    def work_errors(self):
        return [w.error for w in self.works if w.error]

    @property
    def status(self):
        """ """
        if self.withdrawn_at:
            return u"ユーザ取消"
        if self.closed:
            return u"終了"
        if self.canceled_at:
            return u"キャンセル"
        if self.elected_at:
            return u"当選"
        if self.rejected_at:
            return u"落選"
        if self.works:
            return u"当選予定"
        if self.reject_works:
            return u"落選予定"
        return u"申込"

    def elect(self, now):
        now = now or datetime.now()
        self.elected_at = now

    def reject(self, now):
        now = now or datetime.now()
        self.rejected_at = now

    def cancel(self, now):
        now = now or datetime.now()
        self.canceled_at = now

    def withdraw(self, now):
        now = now or datetime.now()
        self.withdrawn_at = now

class LotEntryProduct(LotEntryProductSupport, Base, BaseModel, WithTimestamp, LogicallyDeleted):
    u""" 抽選申し込み商品 """
    __tablename__ = 'LotEntryProduct'

    id = sa.Column(Identifier, primary_key=True)
    quantity = sa.Column(sa.Integer, doc=u"購入予定枚数")

    # 商品
    product_id = sa.Column(Identifier, sa.ForeignKey('Product.id'))
    product = orm.relationship('Product', backref='lot_entry_products')

    # 抽選申し込み希望
    lot_wish_id = sa.Column(Identifier, sa.ForeignKey('LotEntryWish.id'))
    lot_wish = orm.relationship('LotEntryWish', backref='products')

    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'))
    performance = orm.relationship('Performance', backref='lot_entry_products')

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='lot_entry_products')


#class LotElectWork(Base, BaseModel, WithTimestamp, LogicallyDeleted):
class LotElectWork(Base, BaseModel, WithTimestamp):
    """ 当選情報取り込みワーク """
    __tablename__ = 'LotElectWork'

    id = sa.Column(Identifier, primary_key=True)
    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship("Lot", backref="elect_works")
    lot_entry_no = sa.Column(sa.Unicode(20), sa.ForeignKey('LotEntry.entry_no'), unique=True, doc=u"抽選申し込み番号")
    #wish_order = sa.Column(sa.Integer, sa.ForeignKey('LotEntryWish.wish_order'), doc=u"希望順")
    wish_order = sa.Column(sa.Integer, doc=u"希望順")
    entry_wish_no = sa.Column(sa.Unicode(30), doc=u"申し込み番号と希望順を合わせたキー項目")

    error = sa.Column(sa.UnicodeText)

    @property
    def wish(self):
        return LotEntryWish.query.filter(
            LotEntryWish.entry_wish_no==self.entry_wish_no,
        ).one()

    def __repr__(self):
        return "LotEntryProduct {self.entry_wish_no}".format(self=self)


class LotRejectWork(Base, BaseModel, WithTimestamp):
    """ 落選情報取り込みワーク """
    __tablename__ = 'LotRejectWork'

    id = sa.Column(Identifier, primary_key=True)
    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship("Lot", backref="reject_works")
    lot_entry_no = sa.Column(sa.Unicode(20), sa.ForeignKey('LotEntry.entry_no'), unique=True, doc=u"抽選申し込み番号")
    error = sa.Column(sa.UnicodeText)

    @property
    def lot_entry(self):
        return LotEntry.query.filter(
            LotEntry.entry_no==self.lot_entry_no,
        ).one()


    def __repr__(self):
        return "LotRejectProduct {self.entry_wish_no}".format(self=self)


class LotElectedEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 抽選当選情報 """


    __tablename__ = 'LotElectedEntry'

    id = sa.Column(Identifier, primary_key=True)
    lot_entry_id = sa.Column(Identifier, sa.ForeignKey('LotEntry.id'))
    lot_entry = orm.relationship('LotEntry', backref="lot_elected_entries")
    lot_entry_wish_id = sa.Column(Identifier, sa.ForeignKey('LotEntryWish.id'))
    lot_entry_wish = orm.relationship("LotEntryWish", backref="lot_elected_entries")


    mail_sent_at = sa.Column(sa.DateTime)

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))

class LotRejectedEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 抽選落選情報 """


    __tablename__ = 'LotRejectedEntry'

    id = sa.Column(Identifier, primary_key=True)
    lot_entry_id = sa.Column(Identifier, sa.ForeignKey('LotEntry.id'))
    lot_entry = orm.relationship('LotEntry', backref="lot_rejected_entries")

    mail_sent_at = sa.Column(sa.DateTime)


class LotWorkHistory(Base, WithTimestamp):
    __tablename__ = 'LotWorkHistory'

    id = sa.Column(Identifier, primary_key=True)

    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship("Lot", backref="work_histories")
    entry_no = sa.Column(sa.Unicode(20), doc=u"抽選申し込み番号", nullable=False)
    wish_order = sa.Column(sa.Integer, doc=u"希望順")
    error = sa.Column(sa.UnicodeText)

    organization_id = sa.Column(Identifier,
                                sa.ForeignKey('Organization.id'))
    organization = orm.relationship('Organization', backref='lot_work_histories')


class LotEntryAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """抽選で保持するための予約の属性

    ExtraFormで入れた値を保持するためのテーブルです。
    nameには属性名が入ります。valueには購入者が入力したExtraFormの値が入ります。
    """
    __tablename__ = "LotEntryAttribute"
    lot_entry_id = sa.Column(Identifier, sa.ForeignKey('LotEntry.id'), primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode(255), primary_key=True, nullable=False)
    value = sa.Column(sa.Unicode(1023))
