# -*- coding: utf-8 -*-

from ticketing.models import DBSession, Base
from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property
import sqlahelper

session = sqlahelper.get_session()

'''
 Master Data
'''
class Prefecture(Base):
    __tablename__ = 'Prefecture'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    @staticmethod
    def all():
        return session.query(Prefecture).all()

    @staticmethod
    def get(prefecture_id):
        return DBSession.query(Prefecture).filter(Prefecture.id == prefecture_id).first()


class Billing(Base):
    __tablename__ = 'Blling'
    id          = Column(BigInteger, primary_key=True)
    client_id   = Column(BigInteger, ForeignKey('Client.id'))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class ClientTypeEnum(StandardEnum):
    Standard        = 1

class Client(Base):
    __tablename__ = "Client"

    id          = Column(BigInteger, primary_key=True)
    name        = Column(String(255))
    client_type = Column(Integer)
    prefecture_id = Column(BigInteger, ForeignKey("Prefecture.id"), nullable=True)
    prefecture    = relationship("Prefecture", uselist=False)
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

    @staticmethod
    def get(client_id):
        return DBSession.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def update(client):
        session.merge(client)
        session.flush()

    @staticmethod
    def all():
        return session.query(Client).all()

class AccountTypeEnum(StandardEnum):
    Promoter    = 1
    Playguide   = 2
    User        = 3

class Account(Base):
    __tablename__ = "Account"

    id = Column(BigInteger, primary_key=True)

    # @see AccountTypeEnum
    account_type = Column(Integer)

    user_id         = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user            = relationship('User', uselist=False)
    ticketer_id     = Column(BigInteger, ForeignKey("Ticketer.id"), nullable=True)
    ticketer        = relationship("Ticketer", uselist=False)

    updated_at      = Column(DateTime, nullable=True)
    created_at      = Column(DateTime)
    status          = Column(Integer, default=1)

    @staticmethod
    def get(account_id):
        return DBSession.query(Account).filter(Account.id == account_id).first()

class MemberShip(Base):
    '''
      Membership ex) Rakuten Fanclub ....
    '''
    __tablename__ = 'MemberShip'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime)
    status = Column(Integer)

user_table = Table(
    'User', Base.metadata,
    Column('id',             BigInteger, primary_key=True),
    Column('member_ship_id', BigInteger, ForeignKey('MemberShip.id')),
    Column('identifier',     String(255), unique=True),
    Column('email',          String(255)),
    Column('secret_key',     String(255)),
    Column('updated_at',     DateTime),
    Column('created_at',     DateTime),
    Column('status',         Integer, default=1)
)

user_profile_table = Table(
    'User_Profile', Base.metadata,
    Column('id',             BigInteger, primary_key=True),
    Column('nick_name',      String(255)),
    Column('first_name',     String(255)),
    Column('last_name',      String(255)),
    Column('first_name_kana',String(255)),
    Column('last_name_kana', String(255)),
    Column('birth_day',      DateTime),
    Column('sex',            Integer),
    Column('zip',            Integer),
    Column('prefecture_id',  ForeignKey("Prefecture.id")),
    Column('city',           String(255)),
    Column('street',         String(255)),
    Column('address',        String(255)),
    Column('other_address',  String(255)),
    Column('tel_1',          String(255)),
    Column('tel_2',          String(255)),
    Column('fax'  ,          String(255)),
)

class User(Base):
    __table__ = join(user_table, user_profile_table, user_table.c.id == user_profile_table.c.id)
    id = column_property(user_table.c.id, user_profile_table.c.id)

    point_accounts  = relationship("UserPointAccount")
    prefecture      = relationship("Prefecture", uselist=False)
    member_ship     = relationship("MemberShip", uselist=False)

    @staticmethod
    def get(user_id):
        return DBSession.query(User).filter(User.id == user_id).first()

class Ticketer(Base):
    __tablename__ = 'Ticketer'

    id              = Column(BigInteger, primary_key=True)
    zip             = Column(String(255))
    prefecture_id = Column(BigInteger, ForeignKey("Prefecture.id"), nullable=True)
    prefecture    = relationship("Prefecture", uselist=False)
    city            = Column(String(255))
    street          = Column(String(255))
    address         = Column(String(255))
    other_address   = Column(String(255))
    tel_1           = Column(String(32))
    tel_2           = Column(String(32))
    fax             = Column(String(32))

    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

    bank_account_id = Column(BigInteger, ForeignKey('BankAccount.id'))
    bank_account    = relationship('BankAccount', backref='client')

'''
 Oprerator Role & ticketer
'''
operator_role_set_table = Table('OperatorRoleSet', Base.metadata,
    Column('operator_role_id', BigInteger, ForeignKey('OperatorRole.id')),
    Column('operator_id', BigInteger, ForeignKey('Operator.id'))
)

class Permission(Base):
    __tablename__ = 'Permission'
    id = Column(BigInteger, primary_key=True)
    operator_role_id = Column(BigInteger, ForeignKey('OperatorRole.id'))
    operator_role = relationship('OperatorRole', uselist=False)
    category_name = Column(Integer)
    permit = Column(Integer)

class OperatorRole(Base):
    __tablename__ = 'OperatorRole'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    operators = relationship("Operator",
                    secondary=operator_role_set_table)
    permissions = relationship('Permission')
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column('status',Integer, default=1)

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
    Column('expire_at',DateTime, nullable=True),
    Column('updated_at',DateTime),
    Column('created_at',DateTime),
    Column('status',Integer, default=1)
)
operator_auth_table = Table(
    'Operator_Auth', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('login_id', String(32), unique=True),
    Column('password', String(32)),
    Column('auth_code', String(32), nullable=True),
    Column('access_token', String(32), nullable=True),
    Column('secret_key', String(32), nullable=True),
)

class Operator(Base):
    __table__ = join(operator_table, operator_auth_table, operator_table.c.id == operator_auth_table.c.id)
    id = column_property(operator_table.c.id, operator_auth_table.c.id)
    client = relationship('Client',uselist=False)
    roles = relationship("OperatorRole",
        secondary=operator_role_set_table)

    @staticmethod
    def get_by_login_id(user_id):
        return DBSession.query(Operator).filter(Operator.login_id == user_id).first()

performer_association_table = Table('Performer_Performance', Base.metadata,
    Column('performer_id', BigInteger, ForeignKey('Performer.id')),
    Column('performance_id', BigInteger, ForeignKey('Performance.id'))
)

class PerformerCategory(StandardEnum):
    Artist = 1
    Team   = 2

class Performer(Base):
    __tablename__ = 'Performer'
    id = Column(BigInteger, primary_key=True)
    category_code =  Column(Integer)
    name = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class GrantPoint(Base):
    __tablename__ = 'GrantPoint'
    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    point_type_id = Column(BigInteger, ForeignKey('PointType.id'))
    point_type = relationship('PointType', uselist=False)
    
    grant_type  = Column(Integer)
    rate        = Column(DECIMAL)
    fixed       = Column(DECIMAL)

    updated_at  = Column(DateTime)
    created_at  = Column(DateTime)
    status      = Column(Integer)

'''

 Event & Performance

'''
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
    owner_id = Column(BigInteger, ForeignKey('Account.id'))
    owner = relationship('Account')
    performers = relationship('Performer', secondary=performer_association_table)

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
    @staticmethod
    def add(event):
        session.add(event)

    @staticmethod
    def get(event_id):
        return session.query(Event).filter(Event.id==event_id).first()

    @staticmethod
    def update(event):
        session.merge(event)
        session.flush()

    @staticmethod
    def all():
        return session.query(Client).all()

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

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('buyer_condition_id', BigInteger, ForeignKey('BuyerCondition.id')),
    Column('product_id', BigInteger, ForeignKey('Product.id'))
)

class BuyerCondition(Base):
    __tablename__ = 'BuyerCondition'
    id = Column(BigInteger, primary_key=True)

    member_ship_id = Column(BigInteger, ForeignKey('MemberShip.id'))
    member_ship   = relationship('MemberShip')
    '''
     Any Conditions.....
    '''
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)


class Product(Base):
    __tablename__ = 'Product'
    id = Column(BigInteger, primary_key=True)
    buyer_conditions = relationship('BuyerCondition', secondary=buyer_condition_set_table)
    name = Column(String(255))
    price = Column(BigInteger)
    
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    items = relationship('ProductItemMaster', backref='product')

class ProductItemMaster(Base):
    __tablename__ = 'ProductItemMaster'
    id = Column(BigInteger, primary_key=True)
    
    product_id = Column(BigInteger, ForeignKey('Product.id'))

    price = Column(BigInteger)
    item_type = Column(Integer)

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    ticket_type_id = Column(BigInteger, ForeignKey('TicketType.id'))
    ticket_type = relationship('TicketType', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class ProductItem(Base):
    __tablename__ = 'ProductItem'
    id = Column(BigInteger, primary_key=True)

    product_item_master_id = Column(BigInteger, ForeignKey('ProductItemMaster.id'))
    product_item_master = relationship('ProductItemMaster')
    order_item_id = Column(BigInteger, ForeignKey("OrderItem.id"))
    # This can be null if it is a non ticket product
    seat_stock_id = Column(BigInteger, ForeignKey('SeatStock.id'), nullable=True)
    seat_stock = relationship('SeatStock', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

# stock based on quantity
class Stock(Base):
    __tablename__ = "Stock"
    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)
    quantity = Column(Integer)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    @staticmethod
    def get_for_update(pid, stid):
        return session.query(Stock).with_lockmode("update").filter(Stock.performance_id==pid, Stock.seat_type_id==stid).first()

# stock based on phisical seat positions
class SeatStock(Base):
    __tablename__ = "SeatStock"
    id = Column(BigInteger, primary_key=True)
    seat_id = Column(Integer, ForeignKey("SeatMasterL2.seat_id"))
    seat = relationship('SeatMasterL2', uselist=False, backref="seat_stock_id") # 1:1
    sold = Column(Boolean) # sold or not

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    # @TODO
    @staticmethod
    def get_group_seat(pid, stid, num):
        gid = 0
        while True:
            idx = 0
            con_num = 0
            grouping_ss = SeatMasterL2.get_grouping_seat_sets(pid, stid, gid)
            if len(grouping_ss) == 0:
                break
            gid += 1
            for i, gseat in enumerate(grouping_ss):
                if not gseat.sold:
                    if con_num == 0:
                        idx = i
                    con_num += 1
                    if con_num == num:
                        # @TODO return with locked status
                        return grouping_ss[idx:idx+num]
                else:
                    con_num = 0
        return []

class Venue(Base):
    __tablename__ = "Venue"
    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    name = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class VenueBlock(Base):
    __tablename__ = "VenueBlock"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class VenueGate(Base):
    __tablename__ = "VenueGate"
    id = Column(BigInteger, primary_key=True)
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    name = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class VenueFloor(Base):
    __tablename__ = "VenueFloor"
    id = Column(BigInteger, primary_key=True)
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    name = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

# Layer1 SeatMaster
class SeatMaster(Base):
    __tablename__ = "SeatMaster"
    id              = Column(BigInteger, primary_key=True)
    identifieir     = Column(String(255))
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    venue           = relationship('Venue')
    venue_block_id  = Column(BigInteger, ForeignKey('VenueBlock.id'))
    venue_block     = relationship('VenueBlock')
    venue_gate_id   = Column(BigInteger, ForeignKey('VenueGate.id'))
    venue_gate      = relationship('VenueGate')
    venue_floor_id  = Column(BigInteger, ForeignKey('VenueFloor.id'))
    venue_floor     = relationship('VenueFloor')
    col             = Column(String(255))
    row             = Column(String(255))
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

# Layer2 SeatMaster
class SeatMasterL2(Base):
    __tablename__ = "SeatMasterL2"
    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)
    # set a same group id which can be grouping
    group_id = Column(Integer, index=True)
    account_id = Column(BigInteger, ForeignKey('Account.id'))
    account = relationship('Account')
    acconnt_history = relationship('SeatOwneredAccountHistory', backref='seat_masterl2')
    # @TODO have some attributes regarding Layer2
    venue_id = Column(BigInteger)
    seat_id =  Column(BigInteger, ForeignKey('SeatMaster.id'))

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    # @TODO retrieve a record set which have same group_id from 0 to N.
    @staticmethod
    def get_grouping_seat_sets(pid, stid, gid):
        return session.query(SeatMasterL2).filter(SeatMasterL2.performance_id==pid, SeatMasterL2.seat_type_id==stid, SeatMasterL2.group_id==gid).first()

class SeatGroup(Base):
    __tablename__ = "SeatGroup"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)
    
class SeatGroupItem(Base):
    __tablename__ = "SeatGroupItem"
    id = Column(BigInteger, primary_key=True)
    seat_group_id = Column(BigInteger, ForeignKey('SeatGroup.id'))
    seat_group = relationship('SeatGroup')
    seat_id = Column(BigInteger, ForeignKey('SeatMaster.id'))
    seat = relationship('SeatMaster');

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class SeatOwneredAccountHistory(Base):
    __tablename__ = 'SeatOwneredAccountHistory'
    id = Column(BigInteger, primary_key=True)
    seat_masterl2_id = Column(BigInteger, ForeignKey("SeatMasterL2.id"))
    ticket_owner_id = Column(BigInteger, ForeignKey('Account.id'))
    ticket_owner = relationship('Account', primaryjoin="Account.id==SeatOwneredAccountHistory.ticket_owner_id")
    src_ticket_owner_id = Column(BigInteger, ForeignKey('Account.id'), nullable=True)
    src_ticket_owner = relationship('Account', primaryjoin="Account.id==SeatOwneredAccountHistory.src_ticket_owner_id")
    dst_ticket_owner_id = Column(BigInteger, ForeignKey('Account.id'))
    dst_ticket_owner = relationship('Account', primaryjoin="Account.id==SeatOwneredAccountHistory.dst_ticket_owner_id")

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
    bank = relationship("Bank", backref=backref('addresses', order_by=id))
    account_type = Column(Integer)
    account_number = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class PointType(Base):
    __tablename__ = 'PointType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserPointAccount(Base):
    __tablename__ = 'UserPointAccount'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', uselist=False)
    point_type_id = Column(BigInteger, ForeignKey("PointType.id"))
    point_type = relationship('PointType', uselist=False)
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
    expire_at = Column(DateTime)
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
    acrcount_id = Column(BigInteger, ForeignKey("Account.id"))
    account = relationship('Account', uselist=False)
    payment_method_pair_id = Column(BigInteger, ForeignKey('PaymentDeliveryMethodPair.id'))
    payment_method_pair = relationship('PaymentDeliveryMethodPair')

    items = relationship('OrderItem', backref='order')

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class OrderItem(Base):
    __tablename__ = 'OrderItem'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey("Order.id"))
    product_id = Column(BigInteger, ForeignKey("Product.id"))
    product = relationship('Product', uselist=False)
    product_items = relationship('ProductItem', backref='order_item')

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class PaymentMethod(Base):
    __tablename__ = 'PaymentMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class DeliveryMethod(Base):
    __tablename__ = 'DeliveryMethod'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    fee = Column(DECIMAL)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class PaymentDeliveryMethodPair(Base):
    __tablename__ = 'PaymentDeliveryMethodPair'

    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    
    sales_segment_id = Column(BigInteger, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment')

    payment_method_id = Column(BigInteger, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')
    
    delivery_method_id = Column(BigInteger, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod')

    transction_fee = Column(DECIMAL)
    delivery_fee = Column(DECIMAL)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class SalesSegment(Base):
    __tablename__ = 'SalesSegment'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    start_at = Column(DateTime)
    end_at = Column(DateTime)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)


class Auction(Base):
    __tablename__   = 'Auction'
    id              = Column(BigInteger, primary_key=True)
    performance_id  = Column(BigInteger, ForeignKey('Performance.id'))
    performance     = relationship('Performance', uselist=False)
    account_id      = Column(BigInteger, ForeignKey('Account.id'))
    account         = relationship('Account')
    product_item_id = Column(BigInteger, ForeignKey('ProductItem.id'))
    product_item    = relationship('ProductItem')
    start_price     = Column(DECIMAL)
    start_at        = Column(DateTime)
    end_at          = Column(DateTime)
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

class AuctionBidHistory(Base):
    __tablename__   = 'AuctionBidHistory'
    id              = Column(BigInteger, primary_key=True)
    auction_id      = Column(BigInteger, ForeignKey('Auction.id'))
    auction         = relationship('Auction', uselist=False)
    account_id      = Column(BigInteger, ForeignKey('Account.id'))
    account         = relationship('Account', uselist=False)
    price           = Column(DECIMAL)
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)



