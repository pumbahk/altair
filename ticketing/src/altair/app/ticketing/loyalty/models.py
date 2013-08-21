# encoding: utf-8

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode, UnicodeText, TIMESTAMP
from sqlalchemy import util as sautil
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship, aliased
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import event as sa_event
from pyramid.i18n import TranslationString as _
from altair.saannotation import AnnotatedColumn
from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, DBSession
from altair.app.ticketing.core.models import Product, SalesSegment
from standardenum import StandardEnum

SalesSegment_PointGrantSetting = Table(
    'SalesSegment_PointGrantSetting',
    Base.metadata,
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id', onupdate='cascade', ondelete='cascade')),
    Column('point_grant_setting_id', Identifier, ForeignKey('PointGrantSetting.id', onupdate='cascade', ondelete='cascade'))
    )

PointGrantSetting_Product = Table(
    'PointGrantSetting_Product',
    Base.metadata,
    Column('point_grant_setting_id', Identifier, ForeignKey('PointGrantSetting.id', onupdate='cascade', ondelete='cascade')),
    Column('product_id', Identifier, ForeignKey('Product.id', onupdate='cascade', ondelete='cascade')),
    )

class PointGrantSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PointGrantSetting'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), nullable=False)
    organization = relationship('Organization',
        backref='point_grant_settings',
        cascade='all'
        )
    name = AnnotatedColumn(Unicode(255), nullable=False, _a_label=_(u'キャンペーン名'))
    type = AnnotatedColumn(Integer, nullable=False, _a_label=_(u'ポイント種別'))
    fixed = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=True, _a_label=_(u'固定付与ポイント'))
    rate = AnnotatedColumn(Float, nullable=True, _a_label=_(u'ポイント付与率'))
    start_at = AnnotatedColumn(DateTime, _a_label=_(u'開始日時'))
    end_at = AnnotatedColumn(DateTime, _a_label=_(u'終了日時'))
    sales_segments = relationship('SalesSegment',
        secondary='SalesSegment_PointGrantSetting',
        backref='point_grant_settings',
        cascade='all',
        collection_class=set
        )
    target_products = relationship('Product',
        secondary='PointGrantSetting_Product',
        backref='point_grant_settings',
        cascade='all',
        collection_class=set
        )
    target_product_ids = association_proxy('target_products', 'id')

    def applicable_to(self, dt, type=None, product=None):
        return ((self.start_at == None) or (self.start_at < dt)) and \
               ((self.end_at == None) or (dt <= self.end_at)) and \
               (type == None or self.type == type) and \
               (product == None or (product in target_products))

    def __cmp__(self, other):
        if self.start_at is not None:
            if other is None or other.start_at is None or other.start_at < self.start_at:
                return 1
            elif other.start_at > self.start_at:
                return -1
        else:
            if other is not None and other.start_at is not None:
                return -1
        if self.end_at is not None:
            if other is None or other.end_at is None or other.end_at > self.end_at:
                return 1
            elif other.end_at < self.end_at:
                return -1
        else:
            if other is not None and other.end_at is not None:
                return 1
        return cmp(self.id, other.id)

def sales_segment_added_to_point_grant_setting(target, value, initiator):
    target.target_products.update(value.products)

def sales_segment_removed_from_point_grant_setting(target, value, initiator):
    target.target_products.difference_update(value.products)

sa_event.listen(PointGrantSetting.sales_segments, 'append', sales_segment_added_to_point_grant_setting)
sa_event.listen(PointGrantSetting.sales_segments, 'remove', sales_segment_removed_from_point_grant_setting)

def product_added_to_sales_segment(target, value, initiator):
    for point_grant_setting in target.point_grant_settings:
        point_grant_setting.target_products.add(value)

def product_removed_from_sales_segment(target, value, initiator):
    for point_grant_setting in target.point_grant_settings:
        point_grant_setting.target_products.discard(value)

sa_event.listen(SalesSegment.products, 'append', product_added_to_sales_segment)
sa_event.listen(SalesSegment.products, 'remove', product_removed_from_sales_segment)

class PointGrantStatusEnum(StandardEnum):
    InvalidRecord             = 'A001'
    InvalidPointAccountNumber = 'A002'
    InvalidReasonCode         = 'A003'
    InvalidReferenceKey       = 'A004'
    InvalidSubKey             = 'A005'
    InvalidPointValue         = 'A006'
    InvalidShopName           = 'A007'
    NoSuchPointAccount        = 'B001'
    NoSuchReasonCode          = 'B002'
    KeyAlreadyExists          = 'C001'

class PointGrantHistoryEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PointGrantHistoryEntry'
    id = Column(Identifier, primary_key=True)
    user_point_account_id = Column(Identifier, ForeignKey('UserPointAccount.id'))
    user_point_account = relationship('UserPointAccount', uselist=False)
    order_id = Column(Identifier, ForeignKey('Order.id'), nullable=True)
    order = relationship('Order', uselist=False, backref='point_grant_history_entries')
    amount = Column(Numeric(precision=16, scale=2), nullable=False)
    submitted_on = Column(Date, nullable=False)
    grant_status = Column(Unicode(4), nullable=True)
    granted_amount = Column(Numeric(precision=16, scale=2), nullable=True)
    granted_at = Column(DateTime, nullable=True)

