# -*- coding:utf-8 -*-

"""
APIに合わせるためPEP8命名規約に従わない
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted


class CheckoutItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 購入商品情報
    動的商品情報送信APIで利用
    """
    __tablename__ = 'CheckoutItem'

    id = sa.Column(sa.Integer, primary_key=True)
    checkout_id = sa.Column(sa.Integer, sa.ForeignKey('Checkout.id'))
    itemId = sa.Column(sa.String(100))
    itemName = sa.Column(sa.Unicode(255))
    itemNumbers = sa.Column(sa.Integer)
    itemFee = sa.Column(sa.Integer)

    # OrderConfirming機能の場合のみ利用
    checkout_cart_id = sa.Column(sa.Integer, sa.ForeignKey("CheckoutCart.id"))
    itemConfirmationResult = sa.Column(sa.Enum('0', '1', '2', '3'), default='0')
    itemNumbersMessage = sa.Column(sa.Unicode(100))
    itemFeeMessage = sa.Column(sa.Unicode(100))


class Checkout(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 購入情報
    動的商品情報送信APIで利用
    """
    __tablename__ = 'Checkout'

    id = sa.Column(sa.Integer, primary_key=True)
    orderId = sa.Column(sa.Unicode(30))
    orderControlId = sa.Column(sa.Unicode(31))
    orderCartId = sa.Column(sa.Unicode(255))  # sa.ForeignKey('ticketing_carts.id')
    openId = sa.Column(sa.Unicode(128))
    isTMode = sa.Column(sa.Enum('0', '1'))
    usedPoint = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer)
    orderDate = sa.Column(sa.DateTime)
    items = orm.relationship('CheckoutItem', backref="checkout")


class CheckoutCartConfirmation(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 注文情報確認
    CartConfirmingAPIで利用
    """
    __tablename__ = 'CheckoutCartConfirmation'

    id = sa.Column(sa.Integer, primary_key=True)
    openId = sa.Column(sa.Unicode(255))
    carts = orm.relationship('CheckoutCart', backref='checkout_cart_confirmation')


class CheckoutCart(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """ 注文情報確認
    CartConfirmingAPIで利用
    """
    __tablename__ = 'CheckoutCart'

    id = sa.Column(sa.Integer, primary_key=True)
    cart_confirm_id = sa.Column(sa.Integer, sa.ForeignKey('CheckoutCartConfirmation.id'))
    cartConfirmationId = sa.Column(sa.Unicode(28))
    orderCartId = sa.Column(sa.String(255))
    orderItemsTotalFee = sa.Column(sa.Integer)
    isTMode = sa.Column(sa.Enum('0', '1'))
    items = orm.relationship('CheckoutItem', backref="checkout_cart")
