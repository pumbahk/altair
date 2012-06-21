# -*- coding:utf-8 -*-

"""
APIに合わせるためPEP8命名規約に従わない
"""
from datetime import datetime
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

Base = sqlahelper.get_base()

class CheckoutItem(object):
    """ 購入商品情報
    動的商品情報送信APIで利用
    """

    def __init__(self):
        self.id = u'13'
        self.itemId = u'14'
        self.itemName = u'itemName'
        self.itemNumbers = u'1'
        self.itemFee = u'1000'
        self.checkout_id = u'15'
        self.cart_id = u'16'
        self.completed_order_id = u'17'

    '''
    __tablename__ = 'checkout_items'

    id = sa.Column(sa.Integer, primary_key=True)
    itemId = sa.Column(sa.Unicode(100))
    itemName = sa.Column(sa.Unicode(255))
    itemNumbers = sa.Column(sa.Integer) # 最大500
    itemFee = sa.Column(sa.Integer) # 8桁
    checkout_id = sa.Column(sa.Integer, sa.ForeignKey('checkouts.id'))
    cart_id = sa.Column(sa.Integer, sa.ForeignKey('carts.id'))
    completed_order_id = sa.Column(sa.Integer, sa.ForeignKey("completed_orders.id"))

    # OrderConfirming機能 out の場合のみ利用
    itemConfirmationResult = sa.Column(sa.Enum('0', '1', '2', '3'))
    itemNumbersMessage = sa.Column(sa.Unicode(100))
    itemFeeMessage = sa.Column(sa.Unicode(100))

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    '''

class Checkout(object):
    """ 購入情報
    動的商品情報送信APIで利用
    """

    def __init__(self):
        self.id = u'10'
        self.serviceId = u'1000002333'
        self.itemsInfo = [CheckoutItem()]
        self.orderCartId = u'11'
        self.orderCompleteUrl = u'http://www.ticketstar.jp'
        self.orderFailedUrl = u'http://www.ticketstar.jp'
        self.orderTotalFee = u'1000'
        self.authMethod = u'1'
        self.isTMode = u'1'  # 1:test

    '''
    __tablename__ = 'checkouts'
    id = sa.Column(sa.Integer, primary_key=True)

    serviceId = sa.Column(sa.Unicode(10)) # いつも同じ?
    itemsInfo = orm.relationship('CheckoutItem', backref="checkout")

    orderCartId = sa.Column(sa.String(255))
    orderCompleteUrl = sa.Column(sa.Integer)
    orderFailedUrl = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer) # 最大8桁
    authMethod = sa.Column(sa.Enum('1', '2'))
    isTMode = sa.Column(sa.Enum('0', '1'))
    created_at = sa.Column(sa.DateTime, default=datetime.now)
    '''

#class CheckoutCart(Base):
#    __tablename__ = 'checkout_carts'
#    id = sa.Column(sa.Integer, primary_key=True)
#    created_at = sa.Column(sa.DateTime, default=datetime.now)

class CartConfirm(Base):
    """ 注文情報確認 API
    """

    __tablename__ = 'cart_confirms'

    id = sa.Column(sa.Integer, primary_key=True)
    openid = sa.Column(sa.Unicode(255))
    carts = orm.relationship('CheckoutCart', backref='cart_confirm')
    created_at = sa.Column(sa.DateTime, default=datetime.now)

class CheckoutCart(Base):
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
    created_at = sa.Column(sa.DateTime, default=datetime.now)

class CompletedOrder(Base):
    """ 注文通知受取 
    """

    __tablename__ = 'completed_orders'

    id = sa.Column(sa.Integer, primary_key=True)
    orderId = sa.Column(sa.Unicode(30))
    orderControlId = sa.Column(sa.Unicode(31))
    orderCartId = sa.Column(sa.Unicode(255))
    openid = sa.Column(sa.Unicode(128))
    isTMode = sa.Column(sa.Enum('0', '1'))
    usedPoint = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer)
    orderDate = sa.Column(sa.DateTime)
    items = orm.relationship('CheckoutItem')
    created_at = sa.Column(sa.DateTime, default=datetime.now)

class CompletedOrderResult(Base):
    """ 注文通知返信
    """

    __tablename__ = 'completed_order_results'

    id = sa.Column(sa.Integer, primary_key=True)
    result = sa.Column(sa.Enum('0', '1'))
    completeTime = sa.Column(sa.DateTime)
    created_at = sa.Column(sa.DateTime, default=datetime.now)
