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
import ticketing.core.models as c_models
from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.exc import NoResultFound
from zope.deprecation import deprecate

from ticketing.utils import StandardEnum
from ticketing.models import (
    Identifier,
    Base,
    BaseModel,
    WithTimestamp,
    LogicallyDeleted,
    DBSession,
)

from ticketing.core.models import (
    Product,
)
from ticketing.users.models import (
    SexEnum,
)
from ticketing.cart.models import (
    Cart,
)


# 抽選 - 公演
Lot_Performance = sa.Table('Lots_Performance', Base.metadata,
    sa.Column('lot_id', Identifier, sa.ForeignKey('Lot.id')),
    sa.Column('performance_id', Identifier, sa.ForeignKey('Performance.id')),
)

# 抽選 - 席種
Lot_StockType = sa.Table('Lots_StockType', Base.metadata,
    sa.Column('lot_id', Identifier, sa.ForeignKey('Lot.id')),
    sa.Column('stock_type_id', Identifier, sa.ForeignKey('StockType.id')),
)

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

Lot_SalesSegment = sa.Table(
    "Lot_SalesSegment",
    Base.metadata,
    sa.Column("lot_id", Identifier, sa.ForeignKey("Lot.id")),
    sa.Column("sales_segment_id", Identifier, sa.ForeignKey("SalesSegment.id")),
)

class Lot(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Lot'
    
    id = sa.Column(Identifier, primary_key=True)
    name = sa.Column(sa.String(255))

    limit_wishes = sa.Column(sa.Integer, doc=u"希望数")

    event_id = sa.Column(Identifier, sa.ForeignKey('Event.id'))
    event = orm.relationship('Event', backref='lots')

    # performances = orm.relationship('Performance', 
    #     secondary=Lot_Performance)

    # TODO: 席種が必要か確認（商品から辿れるはず）
    stock_types = orm.relationship('StockType',
        secondary=Lot_StockType)

    selection_type = sa.Column(sa.Integer) # LotSelectionEnum

    # sales_segment_group_id = sa.Column(Identifier, sa.ForeignKey('SalesSegmentGroup.id'))
    # sales_segment_group = orm.relationship('SalesSegmentGroup', backref="lots")
    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref="lots")

    status = sa.Column(sa.Integer, default=int(LotStatusEnum.New))

    description = sa.Column(sa.UnicodeText)
    entry_limit = sa.Column(sa.Integer, default=0, server_default="0")

    lotting_announce_datetime = sa.Column(sa.DateTime, doc=u"抽選結果発表予定日")

    system_fee = sa.Column(sa.Numeric(precision=16, scale=2), default=0,
                           server_default="0")

    def is_elected(self):
        return self.status == int(LotStatusEnum.Elected)

    def finish_lotting(self):
        self.status = int(LotStatusEnum.Elected)

    def check_entry_limit(self, email):
        if self.entry_limit <= 0:
            return True

        return LotEntry.query.filter(
            LotEntry.lot_id==self.id
        ).filter(
            LotEntry.shipping_address_id==c_models.ShippingAddress.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            sql.or_(c_models.ShippingAddress.email_1==email,
                    c_models.ShippingAddress.email_2==email)
        ).count() < self.entry_limit


    @hybrid_method
    def available_on(self, now):
        return self.start_at <= now <= self.end_at

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
    def end_at(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.end_at

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
    def upper_limit(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.upper_limit

    @property
    def seat_choice(self):
        if self.sales_segment is None:
            return None
        return self.sales_segment.seat_choice
        
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


class LotEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 抽選申し込み """
    
    __tablename__ = 'LotEntry'
    
    id = sa.Column(Identifier, primary_key=True)

    entry_no = sa.Column(sa.Unicode(20), unique=True, doc=u"抽選申し込み番号")

    # 抽選
    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship('Lot', backref='entries')

    # 申し込み情報
    shipping_address_id = sa.Column(Identifier, sa.ForeignKey('ShippingAddress.id'))
    shipping_address = orm.relationship('ShippingAddress', backref="lot_entries")

    # 申し込み時会員種別
    membergroup_id = sa.Column(Identifier, sa.ForeignKey('MemberGroup.id'))
    membergroup = orm.relationship("MemberGroup", backref="lot_entries")

    elected_at = sa.Column(sa.DateTime)
    rejected_at = sa.Column(sa.DateTime)

    cart_id = sa.Column(Identifier, sa.ForeignKey(Cart.id))
    cart = orm.relationship("Cart", backref="lot_entries")

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))
    order = orm.relationship("Order", backref="lot_entries")

    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey('PaymentDeliveryMethodPair.id'))
    payment_delivery_method_pair = orm.relationship('PaymentDeliveryMethodPair', backref='lot_entries')


    gender = sa.Column(sa.Integer, default=int(SexEnum.NoAnswer))
    birthday = sa.Column(sa.Date)
    memo = sa.Column(sa.UnicodeText)

    canceled_at = sa.Column(sa.DateTime())

    @property
    def max_amount(self):
        """" """
        return max([w.total_amount for w in self.wishes])

    @property
    def status(self):
        retval = LotEntryStatusEnum.New
        if self.rejected_at is not None:
            retval = LotEntryStatusEnum.Rejected
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
    def is_ordered(self):
        return self.is_elected and self.order_id != None

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
        wish.elect(now)
        return elected

    def cancel(self):
        now = datetime.now()
        self.canceled_at = now
        for wish in self.wishes:
            wish.cancel(now)



class LotEntryWish(Base, BaseModel, WithTimestamp, LogicallyDeleted):
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

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))
    order = orm.relationship('Order', backref='lot_wishes')

    canceled_at = sa.Column(sa.DateTime())

    @property
    def transaction_fee(self):
        """ 決済手数料 """
        payment_fee = self.lot_entry.payment_delivery_method_pair.transaction_fee
        payment_method = self.lot_entry.payment_delivery_method_pair.payment_method
        if payment_method.fee_type == c_models.FeeTypeEnum.Once.v[0]:
            return payment_fee
        elif payment_method.fee_type == c_models.FeeTypeEnum.PerUnit.v[0]:
            return payment_fee * self.total_quantity
        else:
            return 0

    @property
    def delivery_fee(self):
        """ 引取手数料 """
        delivery_fee = self.lot_entry.payment_delivery_method_pair.delivery_fee
        delivery_method = self.lot_entry.payment_delivery_method_pair.delivery_method
        if delivery_method.fee_type == c_models.FeeTypeEnum.Once.v[0]:
            return delivery_fee
        elif delivery_method.fee_type == c_models.FeeTypeEnum.PerUnit.v[0]:
            return delivery_fee * self.total_quantity
        else:
            return 0

    @property
    def tickets_amount(self):
        return sum(p.subtotal for p in self.products)

    @property
    def total_amount(self):
        return self.tickets_amount + self.system_fee + self.transaction_fee + self.delivery_fee

    @property
    def total_quantity(self):
        return sum([p.quantity for p in self.products])

    @property
    def system_fee(self):
        #return self.lot_entry.lot.system_fee
        return self.lot_entry.payment_delivery_method_pair.system_fee

    def elect(self, now):
        now = now or datetime.now()
        self.elected_at = now

    def reject(self, now):
        now = now or datetime.now()
        self.rejected_at = now

    def cancel(self, now):
        now = now or datetime.now()
        self.canceled_at = now

class LotEntryProduct(Base, BaseModel, WithTimestamp, LogicallyDeleted):
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

    @property
    def subtotal(self):
        """ 購入額小計
        """
        return self.product.price * self.quantity


class LotElectWork(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 当選情報取り込みワーク """
    __tablename__ = 'LotElectWork'

    id = sa.Column(Identifier, primary_key=True)
    lot_id = sa.Column(Identifier, sa.ForeignKey('Lot.id'))
    lot = orm.relationship("Lot", backref="elect_works")
    lot_entry_no = sa.Column(sa.Unicode(20), sa.ForeignKey('LotEntry.entry_no'), unique=True, doc=u"抽選申し込み番号")
    wish_order = sa.Column(sa.Integer, sa.ForeignKey('LotEntryWish.wish_order'), doc=u"希望順")
    entry_wish_no = sa.Column(sa.Unicode(30), doc=u"申し込み番号と希望順を合わせたキー項目")



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
