# -*- coding:utf-8 -*-
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, Index, UniqueConstraint
from sqlalchemy.orm import join, backref, column_property

from standardenum import StandardEnum
from ticketing.models import relationship
from ticketing.master.models import *
import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class User(Base, WithTimestamp):
    __tablename__ = 'User'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    status = Column(Integer)

    bank_account_id = Column(Identifier, ForeignKey('BankAccount.id'))
    bank_account    = relationship('BankAccount')

    @staticmethod
    def get(user_id):
        return session.query(User).filter(User.id == user_id).first()

    @property
    def first_user_credential(self):
        ## 実態としては、user: user_credentialは1:1だけれど、すでに[0]で取得しているコードなどが存在するので
        return self.user_credential[0]

class Member(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Member'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref=backref("member", uselist=False))
    membergroup_id = Column(Identifier, ForeignKey('MemberGroup.id'))
    membergroup = relationship('MemberGroup', backref='users')

    @classmethod
    def get_or_create_by_member_group(cls, member_group):
        qs = cls.query.filter_by(deleted_at=None, membergroup=membergroup)
        return qs.first() or cls(membergroup=membergroup)

class SexEnum(StandardEnum):
    Male = 1
    Female = 2
    NoAnswer = 0

class UserProfile(Base, BaseModel, WithTimestamp):
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
    country = Column(String(255))
    prefecture = Column(String(64), nullable=False, default=u'')
    city = Column(String(255), nullable=False, default=u'')
    address_1 = Column(String(255), nullable=False, default=u'')
    address_2 = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    status = Column(Integer)

    @property
    def full_name_kana(self):
        return u"%s %s" % (self.last_name_kana,  self.first_name_kana)
    def full_name(self):
        return u"%s %s" % (self.last_name, self.firstname)

class UserCredential(Base, WithTimestamp):
    __tablename__ = 'UserCredential'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)

    auth_identifier = Column(String(255), unique=True)
    auth_secret= Column(String(255))

    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref="user_credential", uselist=False)

    membership_id = Column(Identifier, ForeignKey('Membership.id'))
    membership = relationship("Membership", uselist=False)

    status = Column(Integer)

    @classmethod
    def _filter_by_miscs(cls, qs, membership_id, user_id):
        if membership_id:
            qs = qs.filter_by(membership_id=membership_id)
        if user_id:
            qs = qs.filter_by(user_id=user_id)
        return qs

    @classmethod
    def get_or_create(cls, loginname, password, membership_id=None, user_id=None):
        qs = cls.query.filter_by(deleted_at=None, auth_identifier=loginname, auth_secret=password)
        qs = cls._filter_by_miscs(qs, membership_id, user_id)
        return qs.first() or cls(auth_identifier=loginname, 
                                 auth_secret=password, 
                                 membership_id=membership_id, 
                                 user_id=user_id)
    @classmethod
    def get_or_create_overwrite_password(cls, loginname, password, membership_id=None, user_id=None):
        qs = cls.query.filter_by(deleted_at=None, auth_identifier=loginname)
        qs = cls._filter_by_miscs(qs, membership_id, user_id)
        instance = qs.first()

        if instance:
            instance.auth_secret = password
            return instance

        return cls(auth_identifier=loginname, 
                   auth_secret=password, 
                   membership_id=membership_id, 
                   user_id=user_id)
    
    
        
class UserPointAccount(Base, WithTimestamp):
    __tablename__ = 'UserPointAccount'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref="user_point_account", uselist=False)
    point_type_code = Column(Integer)
    account_number = Column(String(255))
    account_expire = Column(String(255))
    account_owner = Column(String(255))
    status = Column(Integer)

class UserPointHistory(Base, WithTimestamp):
    __tablename__ = 'UserPointHistory'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_point_account_id = Column(Identifier, ForeignKey("UserPointAccount.id"))
    user_point_account = relationship('UserPointAccount', uselist=False)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', uselist=False)
    point = Column(Integer)
    rate = Column(Integer)
    status = Column(Integer)

class MailMagazine(Base, WithTimestamp):
    __tablename__ = 'MailMagazine'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(1024))
    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False, backref='mail_magazines')
    status = Column(Integer)

    def subscribe(self, user, mail_address):
        subscription = MailSubscription.query.filter(
            #MailSubscription.user==user,
            MailSubscription.email==mail_address
        ).filter(
            MailSubscription.segment==self
        ).first()

        # Do nothing if the user is subscribing the magazine
        # with the same e-mail address.
        if subscription:
            return None
        subscription = MailSubscription(email=mail_address, user=user, segment=self)
        session.add(subscription)
        return subscription

    def unsubscribe(self, user, mail_address):
        subscription = MailSubscription.query.filter(
            MailSubscription.user==user,
            MailSubscription.email==mail_address
        ).filter(
            MailSubscription.segment==mailmagazine
        ).first()
        if subscription:
            session.delete(subscription)

class MailSubscription(Base, WithTimestamp):
    __tablename__ = 'MailSubscription'
    __table_args__ = (
        Index('email_segment_idx', 'email', 'segment_id', unique=True),
        )
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    email = Column(String(255))
    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship('User', uselist=False, backref='mail_subscription')
    segment_id = Column(Identifier, ForeignKey("MailMagazine.id"), nullable=True)
    segment = relationship('MailMagazine', uselist=False)

    status = Column(Integer)

class Membership(Base, WithTimestamp):
    '''
      Membership ex) Rakuten Fanclub ....
    '''
    __tablename__ = 'Membership'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    #sales_segments = lambda:relationship('SalesSegment', secondary=Membership_SalesSegment.__table__, backref='memberships')
    status = Column(Integer)

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='memberships')


MemberGroup_SalesSegment = Table('MemberGroup_SalesSegment', Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('membergroup_id', Identifier, ForeignKey('MemberGroup.id')),
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    UniqueConstraint('membergroup_id', 'sales_segment_id'),
)

class MemberGroup(Base, WithTimestamp):
    __tablename__ = 'MemberGroup'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    membership_id = Column(Identifier, ForeignKey('Membership.id'))
    membership = relationship('Membership', backref='membergruops')
    is_guest = Column(Boolean, default=False, server_default='0', nullable=False)

    sales_segments = relationship('SalesSegment',
        secondary=MemberGroup_SalesSegment,
        backref="membergroups")
   
    @classmethod
    def get_or_create_by_name(cls, name, membership_id=None):
        qs = cls.query.filter_by(deleted_at=None, name=name)
        if membership_id:
            qs = qs.filter_by(membership_id=membership_id)
        return qs.first() or cls(name=name, membership_id=membership_id)

# class Membership_SalesSegment(Base):
#     __tablename__ = 'Membership_SalesSegment'
#     query = session.query_property()
#     membership_id = Column(Identifier, ForeignKey('Membership.id'), primary_key=True)
#     sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'), primary_key=True)
