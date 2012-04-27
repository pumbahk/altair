"""
APIに合わせるためPEP8命名規約に従わない
"""
import sqlahelper
import sqlalchemy as sa
import sqlalchemy.orm as orm

Base = sqlahelper.get_base()

class CheckoutItem(object):
    """ 購入情報
    """

    __tablename__ = 'checkout_items'

    id = sa.Column(sa.Integer, primary_key=True)
    itemId = sa.Column(sa.Unicode(100))
    itemName = sa.Column(sa.Unicode(255))
    itemNumbers = sa.Column(sa.Integer) # 最大500
    itemFee = sa.Column(sa.Integer) # 8桁
    checkout_id = sa.Column(sa.Integer, sa.ForeignKey('checkouts.id'))

class CheckoutCart(object):
    __tablename__ = 'checkout_carts'
    id = sa.Column(sa.Integer, primary_key=True)

class Checkout(object):
    __tablename__ = 'checkouts'
    id = sa.Column(sa.Integer, primary_key=True)

    serviceId = sa.Column(sa.Unicode(10)) # いつも同じ?
    itemsInfo = orm.relationship('CheckoutItem', backref="checkout")

    card_id = sa.Column(sa.Integer, sa.ForeignKey('carts.id'))
    orderCompleteUrl = sa.Column(sa.Integer)
    orderFailedUrl = sa.Column(sa.Integer)
    orderTotalFee = sa.Column(sa.Integer) # 最大8桁
    authMethod = sa.Column(sa.Enum())
    isTMode = sa.Column(sa.Enum())
