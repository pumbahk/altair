# -*- coding: utf-8 -*-

from ticketing.models import DBSession, Base
from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, backref, column_property

class ClientTypeEnum(StandardEnum):
    Standard        = 1

class Client(Base):
    __tablename__ = 'Client'
    id = Column(BigInteger, primary_key=True)
    contract_type = Column(Integer)
    name = Column(String(255))
    company_name = Column(String(255))
    section_name = Column(String(255))
    zip_code = Column(String(7))
    country_code = Column(Integer)
    prefecture_code = Column(Integer)
    city = Column(String(32))
    address = Column(String(255))
    street = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    bank_account_id = Column(BigInteger, ForeignKey('BankAccount.id'))
    bank_account = relationship('BankAccount', backref='client')
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user = relationship('User', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

operator_roll_association_table = Table('OperatorRoll_Operator', Base.metadata,
    Column('operator_roll_id', BigInteger, ForeignKey('OperatorRoll.id')),
    Column('operator_id', BigInteger, ForeignKey('Operator.id'))
)

class Permission(Base):
    __tablename__ = 'Permission'
    id = Column(BigInteger, primary_key=True)
    operator_roll_id = Column(BigInteger, ForeignKey('OperatorRoll.id'))
    operator_roll = relationship('OperatorRoll', uselist=False)
    category_code = Column(Integer)
    permit = Column(Integer)

class OperatorRoll(Base):
    __tablename__ = 'OperatorRoll'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    operators = relationship("Operator",
                    secondary=operator_roll_association_table,
                    backref="OperatorRoll")
    permissions = relationship('Permission')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OperatorActionHistory(Base):
    __tablename__ = 'OperatorActionHistory'
    id = Column(BigInteger, primary_key=True)
    function = Column(String(255))
    data = Column(String(1024))
    created_at = Column(DateTime)
    operator_id = Column(BigInteger, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)

operator_table = Table(
    'Operator', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('name', String(255)),
    Column('email',String(255)),
    Column('client_id',BigInteger, ForeignKey('Client.id')),
    Column('updated_at',DateTime),
    Column('created_at',DateTime),
    Column('status',Integer)
)
operator_auth_table = Table(
    'Operator_Auth', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('login_id', String(32)),
    Column('secret_key', String(32))
)

class Operator(Base):
    __table__ = join(operator_table, operator_auth_table, operator_table.c.id == operator_auth_table.c.id)
    id = column_property(operator_table.c.id, operator_auth_table.c.id)
    client = relationship('Client',uselist=False)


class Performance(Base):
    __tablename__ = 'Performance'
    id = Column(BigInteger, primary_key=True)
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)
    no_period = Column(Boolean)
    name = Column(String(255))
    code = Column(String(12))
    client_id = Column(BigInteger, ForeignKey('Client.id'))
    client = relationship('Client', backref='event')

event_table = Table(
    'Event', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('start_on', Date),
    Column('end_on', Date),
    Column('publish_at', DateTime),
    Column('code', String(12)),
    Column('title', String(1024)),
    Column('abbreviated_title', String(1024)),
    Column('margin_ratio', Float),
    Column('printing_fee', Float),
    Column('registration_fee', Float),
    Column('redirect_to_url', String(1024)),
    Column('hidden', Boolean),
    Column('exclude_from_search', Boolean)
    )

event_detail_table = Table(
    'Event_DETAIL', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('seats_and_prices', String(1024))
    )

class Event(Base):
    __table__ = join(event_table, event_detail_table, event_table.c.id == event_detail_table.c.id)
    id = column_property(event_table.c.id, event_detail_table.c.id)
    performances = relationship('Performance', backref='event')

class SeatType(Base):
    __tablename__ = 'SeatType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class TicketType(Base):
    __tablename__ = 'TicketType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', uselist=False)
    price = Column(BigInteger)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class Product(Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    price = Column(BigInteger)
    
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    items = relationship('ProductItem')

class ProductItem(Base):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)
    
    product_id = Column(BigInteger, ForeignKey('Product.id'))
    product = relationship('Product', uselist=False)

    price = Column(BigInteger)
    item_type = Column(Integer)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    ticket_type_id = Column(BigInteger, ForeignKey('TicketType.id'))
    ticket_type = relationship('TicketType', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)

    product_id = Column(BigInteger, ForeignKey('Product.id'))
    product = relationship('Product', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class Bank(Base):
    __tablename__ = 'Bank'
    id = Column(BigInteger, primary_key=True)
    code = Column(BigInteger)
    name = Column(String(255))

class BankAccount(Base):
    __tablename__ = 'BankAccount'
    id = Column(BigInteger, primary_key=True)
    back_id = Column(BigInteger, ForeignKey("Bank.id"))
    account_type = Column(Integer)
    account_number = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
    
class User(Base):
    __tablename__ = 'User'
    id = Column(BigInteger, primary_key=True)
    '''
    OpenID 2.0 : openid.claimed_id
    OpenID 1.1 : openid.identifier
    '''
    open_id_identifier = Column(String(255), unique=True)
    email = Column(String(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birth_day = Column(DateTime)
    sex = Column(Integer)
    zip = Column(String(255))
    prefecture = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
    point_accounts = relationship("UserPointAccount")

class UserPointAccount(Base):
    __tablename__ = 'UserPointAccount'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', uselist=False)
    point_type_code = Column(Integer)
    account_number = Column(String(255))
    account_expire = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserPointHistory(Base):
    __tablename__ = 'UserPointHistory'
    id = Column(BigInteger, primary_key=True)
    user_point_account_id = Column(BigInteger, ForeignKey("UserPointAccount.id"))
    user_point_account = relationship('UserPointAccount', uselist=False)
    point = Column(Integer)
    rate = Column(Integer)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class MailPermission(Base):
    __tablename__ = 'MailPermission'
    id = Column(BigInteger, primary_key=True)
    email = Column(String(255))
    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user = relationship('User', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
    
class ShippingAddress(Base):
    __tablename__ = 'ShippingAddress'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', backref='user_point')
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='shipping_id')
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birth_day = Column(DateTime)
    sex = Column(Integer)
    zip = Column(String(255))
    prefecture = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
    
class Order(Base):
    __tablename__ = 'Order'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', uselist=False)

    items = relationship('OrderItem')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OrderItem(Base):
    __tablename__ = 'OrderItem'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    order = relationship('Order', backref='order_item')
    product_id = Column(BigInteger, ForeignKey("Product.id"))
    product = relationship('Product', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class SeatStock(Base):
    __tablename__ = 'SeatStock'
    id = Column(BigInteger, primary_key=True)
    seat_id = Column(BigInteger)
    venue_id = Column(BigInteger)


