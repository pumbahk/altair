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

from sqlalchemy import sql
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.exc import NoResultFound
from zope.deprecation import deprecate

from ticketing.models import (
    Identifier,
    StandardEnum,
    Base,
    BaseModel,
    WithTimestamp,
    LogicallyDeleted,
)

from ticketing.core.models import (
    Product,
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
    

class Lot(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Lot'
    
    id = sa.Column(Identifier, primary_key=True)
    name = sa.Column(sa.String(255))

    limit_wishes = sa.Column(sa.Integer, doc=u"希望数")

    event_id = sa.Column(Identifier, sa.ForeignKey('Event.id'))
    event = orm.relationship('Event', backref='lots')

    performances = orm.relationship('Performance', 
        secondary=Lot_Performance)

    stock_types = orm.relationship('StockType',
        secondary=Lot_StockType)

    selection_type = sa.Column(sa.Integer) # LotSelectionEnum

    sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'))
    sales_segment = orm.relationship('SalesSegment', backref="lots")

    status = sa.Column(sa.Integer, default=int(LotStatusEnum.New))

    description = sa.Column(sa.UnicodeText)
    entry_limit = sa.Column(sa.Integer, default=0, server_default="0")

    def validate_entry(self, entry):
        return True

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

    cart_id = sa.Column(Identifier, sa.ForeignKey('ticketing_carts.id'))
    cart = orm.relationship("Cart", backref="lot_entries")

    order_id = sa.Column(Identifier, sa.ForeignKey('Order.id'))
    order = orm.relationship("Order", backref="lot_entries")

    payment_delivery_method_pair_id = sa.Column(Identifier, sa.ForeignKey('PaymentDeliveryMethodPair.id'))
    payment_delivery_method_pair = orm.relationship('PaymentDeliveryMethodPair', backref='lot_entries')

    @property
    def is_elected(self):   
        return bool(self.elected_at)

    @property
    def is_rejected(self):
        return bool(self.rejected_at)

    @property
    def is_ordered(self):
        if not self.is_elected:
            return False

        return self.order_id != None

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
    lot_entry = orm.relationship('LotEntry', backref="lot_elected_entries")

    mail_sent_at = sa.Column(sa.DateTime)
