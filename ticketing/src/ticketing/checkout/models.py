# -*- coding:utf-8 -*-

"""
APIに合わせるためPEP8命名規約に従わない
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from ticketing.cart.models import Cart


class CheckoutItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 購入商品情報
    動的商品情報送信APIで利用
    """
    __tablename__ = 'CheckoutItem'

    id = sa.Column(Identifier, primary_key=True)
    checkout_id = sa.Column(Identifier, sa.ForeignKey('Checkout.id'))
    itemId = sa.Column(sa.String(100))
    itemName = sa.Column(sa.Unicode(255))
    itemNumbers = sa.Column(sa.Integer)
    itemFee = sa.Column(sa.Integer)


class Checkout(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 購入情報
    動的商品情報送信APIで利用
    """
    __tablename__ = 'Checkout'

    id = sa.Column(Identifier, primary_key=True)
    orderId = sa.Column(sa.Unicode(30))
    orderControlId = sa.Column(sa.Unicode(31))
    orderCartId = sa.Column(Identifier, sa.ForeignKey(Cart.id))
    openId = sa.Column(sa.Unicode(128))
    isTMode = sa.Column(sa.Enum('0', '1'))
    usedPoint = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer)
    orderDate = sa.Column(sa.DateTime)
    items = orm.relationship('CheckoutItem', backref="checkout")
    cart = orm.relationship('Cart', backref=orm.backref('checkout', uselist=False), uselist=False)
