# -*- coding:utf-8 -*-

"""
APIに合わせるためPEP8命名規約に従わない
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

Base = sqlahelper.get_base()

class CheckoutItem(Base):
    """ 購入商品情報

    動的商品情報送信APIで利用
    """

    __tablename__ = 'checkout_items'

    id = sa.Column(sa.Integer, primary_key=True)
    itemId = sa.Column(sa.Unicode(100))
    itemName = sa.Column(sa.Unicode(255))
    itemNumbers = sa.Column(sa.Integer) # 最大500
    itemFee = sa.Column(sa.Integer) # 8桁
    checkout_id = sa.Column(sa.Integer, sa.ForeignKey('checkouts.id'))
    cart_id = sa.Column(sa.Integer, sa.ForeignKey('carts.id'))

class CheckoutCart(Base):
    __tablename__ = 'checkout_carts'
    id = sa.Column(sa.Integer, primary_key=True)

class Checkout(Base):
    """ 購入情報
    動的商品情報送信APIで利用
    """

    __tablename__ = 'checkouts'
    id = sa.Column(sa.Integer, primary_key=True)

    serviceId = sa.Column(sa.Unicode(10)) # いつも同じ?
    itemsInfo = orm.relationship('CheckoutItem', backref="checkout")

    orderCartId = sa.Column(sa.String(255))
    orderCompleteUrl = sa.Column(sa.Integer)
    orderFailedUrl = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer) # 最大8桁
    authMethod = sa.Column(sa.Enum())
    isTMode = sa.Column(sa.Enum('0', '1'))

class CartConfirm(Base):
    """ 注文情報確認 API
    """

    __tablename__ = 'cart_confirms'

    id = sa.Column(sa.Integer, primary_key=True)
    openid = sa.Column(sa.Unicode(255))
    carts = orm.relationship('Cart', backref='cart_confirm')

class Cart(Base):
    """ 注文情報確認 API
    """

    __tablename__ = 'carts'

    id = sa.Column(sa.Integer, primary_key=True)
    cart_confirm_id = sa.Column(sa.Integer, sa.ForeignKey('cart_confirms.id'))
    cartConfirmationId = sa.Column(sa.Unicode(28))
    orderCartId = sa.Column(sa.String(255))
    orderItemsTotalFee = sa.Column(sa.Integer)
    items = orm.relationship('CheckoutItem', backref="cart_confirm")
    isTMode = sa.Column(sa.Enum('0', '1'))
