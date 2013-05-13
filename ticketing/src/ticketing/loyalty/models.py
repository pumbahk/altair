from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode, UnicodeText, TIMESTAMP
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from standardenum import StandardEnum

SalesSegment_PointGrantSetting = Table(
    'SalesSegment_PointGrantSetting',
    Base.metadata,
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    Column('point_grant_setting_id', Identifier, ForeignKey('PointGrantSetting.id'))
    )

PointGrantSetting_Product = Table(
    'PointGrantSetting_Product',
    Base.metadata,
    Column('point_grant_setting_id', Identifier, ForeignKey('PointGrantSetting.id')),
    Column('product_id', Identifier, ForeignKey('Product.id')),
    )

class PointGrantSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PointGrantSetting'
    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=False)
    organization = relationship('Organization',
        backref='point_grant_settings',
        cascade='all'
        )
    name = Column(Unicode(255), nullable=False)
    type = Column(Integer, nullable=False)
    fixed = Column(Numeric(precision=16, scale=2), nullable=True)
    rate = Column(Float, nullable=True)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    sales_segments = relationship('SalesSegment',
        secondary='SalesSegment_PointGrantSetting',
        backref='point_grant_settings',
        cascade='all',
        collection_class=list
        )
    target_products = relationship('Product',
        secondary='PointGrantSetting_Product',
        backref='point_grant_settings',
        cascade='all',
        collection_class=set
        )

    def applicable_to(self, dt, type, product=None):
        return ((self.start_at == None) or (self.start_at < dt)) and \
               ((self.end_at == None) or (dt <= self.end_at)) and \
               (self.type == type) and \
               (product == None or (not target_products) or (product in target_products))

    def __cmp__(self, other):
        if self.start_at != None:
            if other.start_at > self.start_at:
                return 1
            elif other.start_at < self.start_at:
                return -1
        if self.end_at != None:
            if other.end > self.end:
                return 1
            elif other.end < self.end:
                return -1
        return cmp(self.id, other.id)

class PointGrantStatusEnum(StandardEnum):
    InvalidRecord             = 'A001'
    InvalidPointAccountNumber = 'A002'
    InvalidReasonCode         = 'A003'
    InvalidReferenceKey       = 'A004'
    InvalidSubKey             = 'A005'
    InvalidPointValue         = 'A006'
    InvalidShopNmae           = 'A007'
    NoSuchPointAccount        = 'B001'
    NoSuchReasonCode          = 'B002'
    KeyAlreadyExists          = 'C001'

class PointGrantHistoryEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PointGrantHistoryEntry'
    id = Column(Identifier, primary_key=True)
    user_point_account_id = Column(Identifier, ForeignKey('UserPointAccount.id'))
    user_point_account = relationship('UserPointAccount', uselist=False)
    order_id = Column(Identifier, ForeignKey('Order.id'), nullable=True)
    order = relationship('Order', uselist=False)
    amount = Column(Numeric(precision=16, scale=2), nullable=False)
    submitted_on = Column(Date, nullable=False)
    grant_status = Column(Unicode(4), nullable=True)
    granted_amount = Column(Numeric(precision=16, scale=2), nullable=True)
    granted_at = Column(DateTime, nullable=True)

