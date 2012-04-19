from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property
from ticketing.master.models import *
import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class User(Base):
    __tablename__ = 'User'
    id = Column(BigInteger, primary_key=True)
    email = Column(String(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birth_day = Column(DateTime)
    sex = Column(Integer)
    zip = Column(String(255))
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

    bank_account_id = Column(BigInteger, ForeignKey('BankAccount.id'))
    bank_account    = relationship('BankAccount')

    @staticmethod
    def get(user_id):
        return session.query(User).filter(User.id == user_id).first()

class UserProfile(Base):
    __tablename__ = 'UserProfile'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('User.id'))
    user = relationship('User', backref="user_profile", uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserCredential(Base):
    __tablename__ = 'UserCredential'
    id = Column(BigInteger, primary_key=True)

    auth_identifier = Column(String(1024), unique=True)
    auth_secret= Column(String(1024))

    user_id = Column(BigInteger, ForeignKey('User.id'))
    user = relationship('User', backref="user_credential", uselist=False)

    member_ship_id = Column(BigInteger, ForeignKey('MemberShip.id'))
    member_ship     = relationship("MemberShip", uselist=False)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class UserPointAccount(Base):
    __tablename__ = 'UserPointAccount'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("User.id"))
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
    id = Column(BigInteger, primary_key=True)
    user_point_account_id = Column(BigInteger, ForeignKey("UserPointAccount.id"))
    user_point_account = relationship('UserPointAccount', uselist=False)
    user_id = Column(BigInteger, ForeignKey("User.id"))
    user = relationship('User', uselist=False)
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
