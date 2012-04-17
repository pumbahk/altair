from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()


from ticketing.users.models import User, MemberShip
from ticketing.master.models import BankAccount

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
        return session.query(Account).filter(Account.id == account_id).first()


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
    bank_account    = relationship('BankAccount')

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
    venue_id = Column(BigInteger, ForeignKey('Venue.id'))
    venue = relationship('Venue')

    @staticmethod
    def get(performance_id):
        return session.query(Performance).filter(Performance.id == performance_id).first()

    @staticmethod
    def add(performance):
        session.add(performance)


event_table = Table(
    'Event', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('start_on', Date, nullable=True),
    Column('end_on', Date, nullable=True),
    Column('code', String(12)),
    Column('title', String(1024)),
    Column('abbreviated_title', String(1024)),
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
    def get_by_code(code):
        return session.query(Event).filter(Event.code==code).first()

    @staticmethod
    def update(event):
        session.merge(event)
        session.flush()

    @staticmethod
    def all():
        return session.query(Event).all()


