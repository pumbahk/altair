from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import join, backref, column_property

from standardenum import StandardEnum
from ticketing.models import relationship
from ticketing.master.models import *
import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class User(Base):
    __tablename__ = 'User'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    bank_account_id = Column(Identifier, ForeignKey('BankAccount.id'))
    bank_account    = relationship('BankAccount')

    @staticmethod
    def get(user_id):
        return session.query(User).filter(User.id == user_id).first()

    def subscribe(self, mailmagazine):
        return MailSubscription(email=self.user_profile.email, user=self, segment=mailmagazine)

    def unsubscribe(self, mailmagazine):
        subscription = MailSubscription.query.filter(
            MailSubscription.user==self
        ).filter(
            MailSubscription.segment==mailmagazine
        ).first()
        if subscription:
            session.delete(subscription)


class SexEnum(StandardEnum):
    Male = 1
    Female = 2
    NoAnswer = 0

class UserProfile(Base):
    __tablename__ = 'UserProfile'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref=backref("user_profile", uselist=False))

    email = Column(String(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birth_day = Column(DateTime)
    sex = Column(Integer)
    zip = Column(String(255))
    prefecture    = Column(String(64), nullable=False, default=u'')
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

class UserCredential(Base):
    __tablename__ = 'UserCredential'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)

    auth_identifier = Column(String(255), unique=True)
    auth_secret= Column(String(255))

    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref="user_credential", uselist=False)

    membership_id = Column(Identifier, ForeignKey('MemberShip.id'))
    membership = relationship("MemberShip", uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserPointAccount(Base):
    __tablename__ = 'UserPointAccount'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref="user_point_account", uselist=False)
    point_type_code = Column(Integer)
    account_number = Column(String(255))
    account_expire = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserPointHistory(Base):
    __tablename__ = 'UserPointHistory'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_point_account_id = Column(Identifier, ForeignKey("UserPointAccount.id"))
    user_point_account = relationship('UserPointAccount', uselist=False)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', uselist=False)
    point = Column(Integer)
    rate = Column(Integer)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class MailMagazine(Base):
    __tablename__ = 'MailMagazine'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(1024))
    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class MailSubscription(Base):
    __tablename__ = 'MailSubscription'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    email = Column(String(255))
    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship('User', uselist=False)
    segment_id = Column(Identifier, ForeignKey("MailMagazine.id"), nullable=True)
    segment = relationship('MailMagazine', uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)


class MemberShip(Base):
    '''
      Membership ex) Rakuten Fanclub ....
    '''
    __tablename__ = 'MemberShip'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

    updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime)
    status = Column(Integer)
