from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sa
from sqlalchemy import orm

Base = declarative_base()

Identifier = sa.Integer

class DummyCheckoutObject(object):
    def __init__(self, order_id, total_amount, is_test_mode='0', items=[]):
        self.orderId = order_id
        self.orderCartId = order_id
        self.isTMode = is_test_mode
        self.orderTotalFee = total_amount
        self.items = items

class DummyCheckoutItemObject(object):
    def __init__(self, id, name, quantity, price):
        self.itemId = id
        self.itemName = name
        self.itemNumbers = quantity
        self.itemFee = price

class CheckoutOrder(Base):
    __tablename__ = 'CheckoutOrder'

    id = sa.Column(Identifier, autoincrement=True, primary_key=True)
    service_id = sa.Column(sa.Unicode(16), nullable=False)
    provided_id = sa.Column(sa.Unicode(255), nullable=False)
    openid_claimed_id = sa.Column(sa.Unicode(255), nullable=False)
    order_id = sa.Column(sa.Unicode(30), nullable=False)
    order_control_id = sa.Column(sa.Unicode(30), nullable=False)
    status_id = sa.Column(sa.Unicode(255), nullable=True)
    request_id = sa.Column(sa.Unicode(16), nullable=True)
    test_mode = sa.Column(sa.Integer, nullable=False)
    total_amount = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    used_points = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    order_date = sa.Column(sa.DateTime, nullable=False)

class CheckoutOrderItem(Base):
    __tablename__ = 'CheckoutOrderItem'

    id = sa.Column(Identifier, autoincrement=True, primary_key=True)
    checkout_order_id = sa.Column(Identifier, sa.ForeignKey('CheckoutOrder.id'), nullable=False)
    provided_id = sa.Column(sa.Unicode(100), nullable=False)
    name = sa.Column(sa.Unicode(255), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    price = sa.Column(sa.Numeric(precision=16, scale=2), nullable=False)
    order = orm.relationship(CheckoutOrder, backref=orm.backref('items'))

serial_number_table = sa.Table(
    'SerialNumber', Base.metadata,
    sa.Column('serial', sa.Integer, autoincrement=True, primary_key=True),
    sa.Column('used_for', sa.Unicode(32))
    )
