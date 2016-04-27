# -*- coding:utf-8 -*-
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Unicode, Date, DateTime, ForeignKey, DECIMAL, Index, UniqueConstraint, Text
from sqlalchemy.sql.expression import case, null
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import join, backref, column_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from pyramid.i18n import TranslationString as _
from altair.saannotation import AnnotatedColumn

from standardenum import StandardEnum
from altair.app.ticketing.models import relationship
from altair.app.ticketing.master.models import *
from altair.app.ticketing.utils import is_nonmobile_email_address
import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class User(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'User'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    status = Column(Integer)

    bank_account_id = Column(Identifier, ForeignKey('BankAccount.id'))
    bank_account    = relationship('BankAccount')

    user_point_accounts = relationship('UserPointAccount', backref="user", collection_class=attribute_mapped_collection('type'), cascade='all,delete-orphan')

    @staticmethod
    def get(user_id):
        return session.query(User).filter(User.id == user_id).first()

    @property
    def first_user_credential(self):
        ## 実態としては、user: user_credentialは1:1だけれど、すでに[0]で取得しているコードなどが存在するので
        return self.user_credential[0] if self.user_credential else None

class Member(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'Member'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    auth_identifier = Column(Unicode(64))
    auth_secret= Column(Unicode(64))
    membergroup_id = Column(Identifier, ForeignKey('MemberGroup.id'))
    membergroup = relationship('MemberGroup', backref='users')
    membership_id = Column(Identifier, ForeignKey('Membership.id', name='Member_ibfk_3', ondelete='CASCADE'))
    membership = relationship('Membership')


class SexEnum(StandardEnum):
    Male = 1
    Female = 2
    NoAnswer = 0

class UserProfile(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'UserProfile'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref=backref("user_profile", uselist=False))

    email_1 = Column(Unicode(255))
    email_2 = Column(Unicode(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    birthday = Column(DateTime)
    sex = Column(Integer)
    zip = Column(Unicode(32))
    country = Column(Unicode(255))
    prefecture = Column(Unicode(64), nullable=False, default=u'')
    city = Column(Unicode(255), nullable=False, default=u'')
    address_1 = Column(Unicode(255), nullable=False, default=u'')
    address_2 = Column(Unicode(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    status = Column(Integer)

    rakuten_point_account = Column(String(20))

    subscribe_word = Column(Boolean(), default=True)

    @hybrid_property
    def full_name_kana(self):
        return self.last_name_kana + u' ' + self.first_name_kana

    @hybrid_property
    def full_name(self):
        return self.last_name + u' ' + self.first_name

    @hybrid_property
    def email(self):
        return self.email_1 or self.email_2

    @email.expression
    def email_expr(self):
        return case([
            (self.email_1 != None, self.email_1),
            (self.email_2 != None, self.email_2)
            ],
            else_=null())

    @property
    def emails(self):
        retval = []
        if self.email_1:
            retval.append(self.email_1)
        if self.email_2:
            retval.append(self.email_2)
        return retval

    @property
    def email_pc(self):
        if self.email_1 and is_nonmobile_email_address(self.email_1):
            return self.email_1
        if self.email_2 and is_nonmobile_email_address(self.email_2):
            return self.email_2
        return None

    @property
    def email_mobile(self):
        if self.email_1 and not is_nonmobile_email_address(self.email_1):
            return self.email_1
        if self.email_2 and not is_nonmobile_email_address(self.email_2):
            return self.email_2
        return None

class UserCredential(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'UserCredential'
    __table_args__= (
        UniqueConstraint("auth_identifier", "membership_id", "deleted_at", name="ib_unique_1"), 
        )
    query = session.query_property()
    id = Column(Identifier, primary_key=True)

    auth_identifier = Column(String(128))
    authz_identifier = Column(String(96))
    auth_secret= Column(String(255))

    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref="user_credential", uselist=False)

    membership_id = Column(Identifier, ForeignKey('Membership.id'))
    membership = relationship("Membership", uselist=False)

    status = Column(Integer)

    @classmethod
    def _filter_by_miscs(cls, qs, membership_id, user):
        if membership_id:
            qs = qs.filter_by(membership_id=membership_id)
        if user:
            qs = qs.filter_by(user=user)
        return qs

    @classmethod
    def get_or_create(cls, auth_identifier, auth_secret, membership_id=None, user=None):
        qs = cls.query.filter_by(auth_identifier=auth_identifier, auth_secret=auth_secret)
        qs = cls._filter_by_miscs(qs, membership_id, user)
        return qs.first() or cls(auth_identifier=auth_identifier, 
                                 auth_secret=auth_secret, 
                                 membership_id=membership_id, 
                                 user=user)
    @classmethod
    def get_or_create_overwrite_password(cls, auth_identifier, auth_secret, membership_id=None, user=None):
        qs = cls.query.filter_by(auth_identifier=auth_identifier)
        qs = cls._filter_by_miscs(qs, membership_id, user)
        instance = qs.first()

        if instance:
            instance.auth_secret = auth_secret
            return instance

        return cls(auth_identifier=auth_identifier, 
                   auth_secret=auth_secret, 
                   membership_id=membership_id, 
                   user=user)
   
class UserPointAccountTypeEnum(StandardEnum):
    Rakuten = 1

class UserPointAccountStatusEnum(StandardEnum):
    Suspended = -1
    Invalid = 0
    Valid = 1

class UserPointAccount(Base, WithTimestamp):
    __tablename__ = 'UserPointAccount'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    type = Column(Integer)
    account_number = Column(String(255))
    account_expire = Column(String(255))
    account_owner = Column(String(255))
    status = Column(Integer)

class Membership(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    '''
      Membership ex) Rakuten Fanclub ....
    '''
    __tablename__ = 'Membership'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    display_name = AnnotatedColumn(String(255), _a_label=_(u'表示名'))
    enable_auto_input_form = AnnotatedColumn(Boolean, default=True, server_default='1', nullable=False, _a_label=_(u'自動フォーム入力'))
    enable_point_input = AnnotatedColumn(Boolean, default=True, server_default='1', nullable=False, _a_label=_(u'楽天ポイント手入力'))
    #sales_segments = lambda:relationship('SalesSegment', secondary=Membership_SalesSegment.__table__, backref='memberships')
    status = Column(Integer)

    memo = Column(Text)
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='memberships')


MemberGroup_SalesSegment = Table('MemberGroup_SalesSegment', Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('membergroup_id', Identifier, ForeignKey('MemberGroup.id')),
    Column('sales_segment_group_id', Identifier, ForeignKey('SalesSegmentGroup.id')),
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    UniqueConstraint('membergroup_id', 'sales_segment_group_id'),
)

MemberGroup_SalesSegmentGroup = Table('MemberGroup_SalesSegmentGroup', Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('membergroup_id', Identifier, ForeignKey('MemberGroup.id')),
    Column('sales_segment_group_id', Identifier, ForeignKey('SalesSegmentGroup.id')),
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    UniqueConstraint('membergroup_id', 'sales_segment_group_id'),
)

class MemberGroup(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'MemberGroup'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = AnnotatedColumn(String(255), _a_label=_(u'会員区分名'))
    membership_id = AnnotatedColumn(Identifier, ForeignKey('Membership.id'), _a_label=_(u'会員種別'))
    membership = relationship('Membership', backref='membergroups')
    is_guest = AnnotatedColumn(Boolean, default=False, server_default='0', nullable=False, _a_label=_(u'ゲストログイン'))

    sales_segment_groups = relationship('SalesSegmentGroup',
        secondary=MemberGroup_SalesSegmentGroup,
        backref="membergroups")

    sales_segments = relationship('SalesSegment',
        secondary=MemberGroup_SalesSegment,
        backref="membergroups")
   
    @classmethod
    def get_or_create_by_name(cls, name, membership_id=None):
        qs = cls.query.filter_by(name=name)
        if membership_id:
            qs = qs.filter_by(membership_id=membership_id)
        return qs.first() or cls(name=name, membership_id=membership_id)

# class Membership_SalesSegment(Base):
#     __tablename__ = 'Membership_SalesSegment'
#     query = session.query_property()
#     membership_id = Column(Identifier, ForeignKey('Membership.id'), primary_key=True)
#     sales_segment_group_id = Column(Identifier, ForeignKey('SalesSegment.id'), primary_key=True)

class WordSubscription(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'WordSubscription'

    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey('User.id'))
    user = relationship('User', backref='wordsubscriptions')
    word_id = Column(Integer)