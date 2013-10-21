# encoding: utf-8
import logging
import itertools
import operator
import json
import re
import sys
from math import floor
import isodate
from datetime import datetime, date, timedelta
import smtplib
from decimal import Decimal

from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
from altair.sqla import association_proxy_many
from sqlalchemy.sql import functions as sqlf
from sqlalchemy import Table, Column, ForeignKey, func, or_, and_, event
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.util import warn_deprecated
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode, UnicodeText, TIMESTAMP, Time
from sqlalchemy.orm import join, backref, column_property, joinedload, deferred, relationship, aliased
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import asc, desc, exists, select, table, column, case, null, alias
from sqlalchemy.ext.associationproxy import association_proxy
from zope.interface import implementer
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _

from zope.deprecation import deprecation

from .exceptions import InvalidStockStateError
from .interfaces import ISalesSegmentQueryable

from altair.app.ticketing.models import (
    Base, DBSession, 
    MutationDict, JSONEncodedDict, 
    LogicallyDeleted, Identifier, DomainConstraintError, 
    WithTimestamp, BaseModel,
    is_any_of
)
from standardenum import StandardEnum
from altair.app.ticketing.users.models import User, UserCredential, MemberGroup, MemberGroup_SalesSegment
from altair.app.ticketing.sej.api import get_sej_order
from altair.app.ticketing.utils import tristate, is_nonmobile_email_address, sensible_alnum_decode, todate, todatetime
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.venues.interfaces import ITentativeVenueSite
from .utils import ApplicableTicketsProducer

logger = logging.getLogger(__name__)

class FeeTypeEnum(StandardEnum):
    Once = (0, u'1件あたりの手数料')
    PerUnit = (1, u'1枚あたりの手数料')

class Seat_SeatAdjacency(Base):
    __tablename__ = 'Seat_SeatAdjacency2'
    l0_id = Column(Unicode(48), ForeignKey('Seat.l0_id'), primary_key=True)
    seat_adjacency_id = Column(Identifier, ForeignKey('SeatAdjacency.id', ondelete='CASCADE'), primary_key=True, nullable=False)

@implementer(ITentativeVenueSite)
class Site(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Site"
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    zip = Column(String(255))
    prefecture   = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    _drawing_url = Column('drawing_url', String(255))
    _frontend_metadata_url = Column('metadata_url', String(255))
    _backend_metadata_url = Column('backend_metadata_url', String(255))

class VenueArea_group_l0_id(Base):
    __tablename__   = "VenueArea_group_l0_id"
    venue_id = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    group_l0_id = Column(Unicode(48), ForeignKey('Seat.group_l0_id', onupdate=None, ondelete='CASCADE'), primary_key=True, nullable=True)
    venue_area_id = Column(Identifier, ForeignKey('VenueArea.id', ondelete='CASCADE'), index=True, primary_key=True, nullable=False)
    venue = relationship('Venue')

class Venue(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Venueは、Performance毎に1個つくられる。
    Venueのテンプレートは、performance_idがNoneになっている。
    """
    __tablename__ = "Venue"
    id = Column(Identifier, primary_key=True)
    site_id = Column(Identifier, ForeignKey("Site.id"), nullable=False)
    performance_id = Column(Identifier, ForeignKey("Performance.id", ondelete='CASCADE'), nullable=True)
    organization_id = Column(Identifier, ForeignKey("Organization.id", ondelete='CASCADE'), nullable=False)
    name = AnnotatedColumn(String(255), _a_label=(u"会場名"))
    sub_name = Column(String(255))

    original_venue_id = Column(Identifier, ForeignKey("Venue.id"), nullable=True)
    derived_venues = relationship("Venue",
                                  backref=backref(
                                    'original_venue', remote_side=[id]))

    site = relationship("Site", uselist=False)
    areas = relationship("VenueArea", backref='venues', secondary=VenueArea_group_l0_id.__table__)
    organization = relationship("Organization", backref='venues')
    seat_index_types = relationship("SeatIndexType", backref='venue')
    attributes = deferred(Column(MutationDict.as_mutable(JSONEncodedDict(16384))))

    @hybrid_property
    def adjacency_sets(self):
        return self.site.adjacency_sets

    @staticmethod
    def create_from_template(template, performance_id, original_performance_id=None):
        # 各モデルのコピー元/コピー先のidの対比表
        convert_map = {
            'seat_adjacency':dict(),
            'seat_index_type':dict(),
        }

        # create Venue
        logger.info('[copy] Venue start')
        venue = Venue.clone(template)
        venue.original_venue_id = template.id
        venue.performance_id = performance_id
        venue.save()
        logger.info('[copy] Venue end')

        # create VenueArea - VenueArea_group_l0_id
        logger.info('[copy] VenueArea start')
        for template_area in template.areas:
            VenueArea.create_from_template(template=template_area, venue_id=venue.id)
        logger.info('[copy] VenueArea end')

        # create SeatIndexType
        logger.info('[copy] SeatIndexType start')
        for template_seat_index_type in template.seat_index_types:
            convert_map['seat_index_type'].update(
                SeatIndexType.create_from_template(template=template_seat_index_type, venue_id=venue.id)
            )
        logger.info('[copy] SeatIndexType end')

        # Performanceのコピー時に配席情報があるならstockのリレーションをコピー
        if original_performance_id and venue.original_venue_id:
            # stock_idのマッピングテーブル
            convert_map['stock_id'] = dict()
            old_stocks = Stock.filter_by(performance_id=template.performance_id).all()
            for old_stock in old_stocks:
                new_stock_id = Stock.filter_by(performance_id=performance_id)\
                    .filter_by(stock_holder_id=old_stock.stock_holder_id)\
                    .filter_by(stock_type_id=old_stock.stock_type_id)\
                    .with_entities(Stock.id).scalar()
                convert_map['stock_id'][old_stock.id] = new_stock_id

        # create Seat - SeatAttribute, SeatStatus, SeatIndex
        logger.info('[copy] Seat - SeatAttribute, SeatStatus, SeatIndex start')
        default_stock = Stock.get_default(performance_id=performance_id)
        for template_seat in template.seats:
            # create Seat
            seat = Seat.clone(template_seat)
            seat.venue_id = venue.id
            if 'stock_id' in convert_map and template_seat.stock:
                seat.stock_id = convert_map['stock_id'][template_seat.stock.id]
            else:
                seat.stock_id = default_stock.id
            for template_attribute in template_seat.attributes:
                seat[template_attribute] = template_seat[template_attribute]
            seat.created_at = datetime.now()
            seat.updated_at = datetime.now()

            # create SeatStatus
            seat.status_ = SeatStatus(status=SeatStatusEnum.Vacant.v)

            # create SeatIndex
            seat_indexes = []
            for template_seat_index in template_seat.indexes:
                seat_index = SeatIndex.clone(template_seat_index)
                if 'seat_index_type' in convert_map:
                    seat_index.seat_index_type_id = convert_map['seat_index_type'][template_seat_index.seat_index_type_id]
                seat_indexes.append(seat_index)
            seat.indexes = seat_indexes

            DBSession.add(seat)
        logger.info('[copy] Seat - SeatAttribute, SeatStatus, SeatIndex end')

    def delete_cascade(self):
        # delete Seat
        for seat in self.seats:
            seat.delete_cascade()

        # delete VenueArea
        for area in self.areas:
            area.delete_cascade()

        # delete Venue
        self.delete()

class VenueArea(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "VenueArea"
    id              = Column(Identifier, primary_key=True)
    name            = Column(String(255), nullable=False)
    groups          = relationship('VenueArea_group_l0_id', backref='area')

    @staticmethod
    def create_from_template(template, **kwargs):
        # create VenueArea
        area = VenueArea.clone(template)
        if 'venue_id' in kwargs:
            area.venue_id = kwargs['venue_id']
        area.save()

        # create VenueArea_group_l0_id
        for template_group in template.groups:
            group = VenueArea_group_l0_id(
                group_l0_id=template_group.group_l0_id,
                venue_id=area.venue_id,
                venue_area_id=area.id
            )
            DBSession.add(group)

    def delete_cascade(self):
        # VenueArea_group_l0_id cannot delete because LogicallyDeleted Seat

        # delete VenueArea
        self.delete()

class SeatAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "SeatAttribute"
    seat_id         = Column(Identifier, ForeignKey('Seat.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    name            = Column(String(255), primary_key=True, nullable=False)
    value           = Column(String(1023))

class Seat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "Seat"

    id              = Column(Identifier, primary_key=True)
    l0_id           = Column(Unicode(48))
    name            = Column(Unicode(50), nullable=False, default=u"", server_default=u"")
    seat_no         = Column(String(255))
    stock_id        = Column(Identifier, ForeignKey('Stock.id'))

    venue_id        = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    row_l0_id       = Column(Unicode(48), index=True)
    group_l0_id     = Column(Unicode(48), index=True)

    venue           = relationship("Venue", backref='seats')
    stock           = relationship("Stock", backref='seats')

    attributes_     = relationship("SeatAttribute", backref='seat', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    areas           = relationship("VenueArea",
                                   primaryjoin=lambda:and_(
                                       Seat.venue_id==VenueArea_group_l0_id.venue_id,
                                       Seat.group_l0_id==VenueArea_group_l0_id.group_l0_id),
                                   secondary=VenueArea_group_l0_id.__table__,
                                   secondaryjoin=VenueArea_group_l0_id.venue_area_id==VenueArea.id,
                                   backref="seats")
    adjacencies     = relationship("SeatAdjacency",
                                   primaryjoin=lambda:Seat.l0_id==Seat_SeatAdjacency.l0_id,
                                   secondary=Seat_SeatAdjacency.__table__,
                                   secondaryjoin=lambda: \
                                     (Seat_SeatAdjacency.seat_adjacency_id==SeatAdjacency.id) & \
                                     (SeatAdjacency.adjacency_set_id == SeatAdjacencySet.id) & \
                                     (SeatAdjacencySet.site_id == Venue.site_id) & \
                                     (Venue.id==Seat.venue_id),
                                   backref="seats")
    status_ = relationship('SeatStatus', uselist=False, backref='seat', cascade='all,delete-orphan') # 1:1

    status = association_proxy('status_', 'status')

    attributes = association_proxy('attributes_', 'value', creator=lambda k, v: SeatAttribute(name=k, value=v))

    def __setitem__(self, name, value):
        self.attributes[name] = value

    def __getitem__(self, name):
        return self.attributes[name]

    def get_index(self, index_type_id):
        return DBSession.query(SeatIndex).filter_by(seat=self, index_type_id=index_type_id)

    def is_hold(self, stock_holder):
        return self.stock.stock_holder == stock_holder

    @classmethod
    def query_sales_seats(cls, sales_segment):
        return cls.query.filter(
                cls.stock_id==ProductItem.stock_id
            ).filter(
                ProductItem.product_id==Product.id
            ).filter(
                Product.sales_segment_id==sales_segment.id
            )

    def delete_cascade(self):
        # delete SeatStatus
        seat_status = SeatStatus.filter_by(seat_id=self.id).first()
        if seat_status:
            seat_status.delete()

        # delete SeatAttribute
        seat_attributes = SeatAttribute.filter_by(seat_id=self.id).all()
        for attribute in seat_attributes:
            attribute.delete()

        # delete Seat
        self.delete()

    # @TODO
    @staticmethod
    def get_grouping_seat_sets(pid, stid):
        return [[]]

class SeatStatusEnum(StandardEnum):
    NotOnSale = 0
    Vacant = 1
    Keep = 8  # インナー予約で座席確保した状態、カート生成前
    Import = 9  # 予約インポートで座席確保した状態、カート生成前
    InCart = 2
    Ordered = 3
    Confirmed = 4
    Shipped = 5
    Canceled = 6
    Reserved = 7

class SeatStatus(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SeatStatus"
    seat_id = Column(Identifier, ForeignKey("Seat.id", ondelete='CASCADE'), primary_key=True)
    status = Column(Integer)

    @staticmethod
    def get_for_update(stock_id):
        return DBSession.query(SeatStock).with_lockmode("update").filter(SeatStatus.seat.stock==stock_id, SeatStatus.status==SeatStatusEnum.Vacant.v).first()

    # @TODO
    @staticmethod
    def get_group_seat(pid, stid, num):
        idx = 0
        con_num = 0
        grouping_ss = Seat.get_grouping_seat_sets(pid, stid)
        for grouping_seats in grouping_ss:
            for i, gseat in enumerate(grouping_seats):
                if not gseat.sold:
                    if con_num == 0:
                        idx = i
                    con_num += 1
                    if con_num == num:
                        # @TODO return with locked status
                        return gseat[idx:idx+num]
                else:
                    con_num = 0
        return []

class SeatAdjacency(Base, BaseModel):
    __tablename__ = "SeatAdjacency"
    query = DBSession.query_property()
    id = Column(Identifier, primary_key=True)
    adjacency_set_id = Column(Identifier, ForeignKey('SeatAdjacencySet.id', ondelete='CASCADE'))

    def seats_filter_by_venue(self, venue_id):
        query = Seat.query.filter(Seat.venue_id == venue_id) \
            .join(Seat_SeatAdjacency, Seat.l0_id == Seat_SeatAdjacency.l0_id) \
            .join(SeatAdjacency, Seat_SeatAdjacency.seat_adjacency_id == SeatAdjacency.id) \
            .join(SeatAdjacencySet, SeatAdjacencySet.id == SeatAdjacency.adjacency_set_id) \
            .join(Venue, Venue.id == Seat.venue_id) \
            .filter(SeatAdjacencySet.site_id == Venue.site_id) \
            .filter(SeatAdjacency.id == self.id)

        return query.all()

class SeatAdjacencySet(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SeatAdjacencySet"
    id = Column(Identifier, primary_key=True)
    site_id = Column(Identifier, ForeignKey('Site.id', ondelete='CASCADE'))
    site = relationship('Site', backref='adjacency_sets')
    seat_count = Column(Integer, nullable=False)
    adjacencies = relationship("SeatAdjacency", backref='adjacency_set')

    def delete(self):
        query = SeatAdjacency.__table__.delete(SeatAdjacency.adjacency_set_id==self.id)
        DBSession.execute(query)
        super(type(self), self).delete()

class AccountTypeEnum(StandardEnum):
    Promoter    = (1, u'プロモーター')
    Playguide   = (2, u'プレイガイド')
    User        = (3, u'ユーザー')

class Account(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Account"
    id = Column(Identifier, primary_key=True)
    account_type = Column(Integer)  # @see AccountTypeEnum
    name = Column(String(255))

    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship('User')

    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False, backref='accounts')
    stock_holders = relationship('StockHolder', backref='account')

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.events:
            raise DomainConstraintError(u'関連づけされたイベントがある為、削除できません')
        if self.stock_holders:
            raise DomainConstraintError(u'関連づけされた枠がある為、削除できません')

        super(Account, self).delete()

    @property
    def account_type_label(self):
        for account_type in AccountTypeEnum:
            if account_type.v[0] == self.account_type:
                return account_type.v[1]
        return

    @staticmethod
    def filter_by_organization_id(id):
        return Account.filter(Account.organization_id==id).all()

@implementer(ISalesSegmentQueryable)
class Performance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Performance'

    id = Column(Identifier, primary_key=True)
    name = AnnotatedColumn(String(255), _a_label=(u'名称'))
    code = Column(String(12))  # Organization.code(2桁) + Event.code(3桁) + 7桁(デフォルトはstart.onのYYMMDD+ランダム1桁)
    abbreviated_title = Column(Unicode(255), doc=u"公演名略称", default=u"")
    subtitle = Column(Unicode(255), doc=u"公演名副題", default=u"")
    note = Column(UnicodeText, doc=u"公演名備考", default=u"")

    open_on = AnnotatedColumn(DateTime, _a_label=(u"開場"))
    start_on = AnnotatedColumn(DateTime, _a_label=(u"開演"))
    end_on = AnnotatedColumn(DateTime, _a_label=(u"終了"))
    public = Column(Boolean, nullable=False, default=False)  # 一般公開するか

    event_id = Column(Identifier, ForeignKey('Event.id'))

    stocks = relationship('Stock', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    venue = relationship('Venue', uselist=False, backref='performance')

    redirect_url_pc = Column(String(1024))
    redirect_url_mobile = Column(String(1024))

    display_order = AnnotatedColumn(Integer, nullable=False, default=1, _a_label=_(u'表示順'))

    @property
    def setting(self):
        return self.settings[0] if self.settings else None

    @property
    def products(self):
        return self.sale_segment.products if self.sales_segment_id else []

    @property
    def stock_types(self):
        return sorted(list({s.stock_type for s in self.stocks if s.stock_type}),
                      key=lambda s: s.id)

    def add(self):
        logger.info('[copy] Stock start')
        BaseModel.add(self)

        origin_venue = None
        if hasattr(self, 'create_venue_id') and self.venue_id:
            origin_venue = Venue.get(self.venue_id)

        if hasattr(self, 'original_id') and self.original_id and origin_venue and origin_venue.original_venue_id:
            """
            配席済みのVenueのコピー時は以下のモデルをcloneする
              - Stock
                - ProductItem
            """
            template_performance = Performance.get(self.original_id)

            # create Stock - ProductItem
            for template_stock in template_performance.stocks:
                Stock.create_from_template(template=template_stock, performance_id=self.id)
        else:
            """
            Venueの作成時は以下のモデルを自動生成する
              - Stock
                - ProductItem
            """
            # create default Stock
            Stock.create_default(self.event, performance_id=self.id)
        logger.info('[copy] Stock end')

    def save(self):
        BaseModel.save(self)

        """
        Performanceの作成/更新時は以下のモデルを自動生成する
        またVenueの変更があったら関連モデルを削除する
          - PerformanceSetting
          - SalesSegment
            - Product
            − MemberGroup_SalesSegment
          - Venue
            - VenueArea
              - VenueArea_group_l0_id
            - SeatIndexType
            - Seat
              - SeatAttribute
              - SeatStatus
              - SeatIndex
        """

        if hasattr(self, 'original_id') and self.original_id:
            logger.info('[copy] SalesSegment start')
            template_performance = Performance.get(self.original_id)

            # create PerformanceSetting
            if template_performance.settings:
                for setting in template_performance.settings:
                    new_setting = PerformanceSetting.create_from_template(setting, performance_id=self.id)
                    new_setting.performance = self

            # create SalesSegment - Product
            for template_sales_segment in template_performance.sales_segments:
                convert_map = {
                    'sales_segment':dict(),
                    'product':dict(),
                }
                convert_map['sales_segment'].update(
                    SalesSegment.create_from_template(template=template_sales_segment, performance_id=self.id)
                )
                template_products = Product.query.filter_by(sales_segment_id=template_sales_segment.id)\
                                                 .filter_by(performance_id=template_performance.id).all()
                for template_product in template_products:
                    convert_map['product'].update(
                        Product.create_from_template(template=template_product, performance_id=self.id, **convert_map)
                    )

                # 関連テーブルのproduct_idを書き換える
                for org_id, new_id in convert_map['product'].iteritems():
                    ProductItem.filter_by(product_id=org_id)\
                               .filter_by(performance_id=self.id)\
                               .update({'product_id':new_id})
            logger.info('[copy] SalesSegment end')

        # create Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'create_venue_id') and self.venue_id:
            template_venue = Venue.query.filter_by(id=self.venue_id).options(
                joinedload(Venue.seats, Seat.indexes),
                joinedload(Venue.seats, Seat.attributes_),
            ).first()
            Venue.create_from_template(
                template=template_venue,
                performance_id=self.id,
                original_performance_id=self.original_id
            )

        # delete Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'delete_venue_id') and self.delete_venue_id:
            logger.info('[delete] Venue start')
            venue = Venue.get(self.delete_venue_id)
            if venue:
                venue.delete_cascade()
            logger.info('[delete] Venue end')

        # defaultのStockに未割当の席数をセット (Venue削除後にカウントする)
        default_stock = Stock.get_default(performance_id=self.id)
        default_stock.quantity = Seat.query.filter(Seat.stock_id==default_stock.id).count()
        default_stock.save()

    def delete(self):

        if self.public:
            raise Exception(u'公開中の為、削除できません')

        if len(self.orders) > 0:
            raise Exception(u'購入されている為、削除できません')

        if len(self.product_items) > 0:
            raise Exception(u'商品詳細がある為、削除できません')

        allocation = Stock.filter(Stock.performance_id==self.id) \
            .filter(Stock.stock_holder_id != None) \
            .with_entities(func.sum(Stock.quantity)).scalar()

        if allocation > 0:
            raise Exception(u'配席されている為、削除できません')

        # delete PerformanceSetting
        for setting in self.settings:
            setting.delete()

        # delete SalesSegment
        for sales_segment in self.sales_segments:
            sales_segment.delete()

        # delete ProductItem
        for product_item in self.product_items:
            product_item.delete()

        # delete Stock
        for stock in self.stocks:
            stock.delete(force=True)

        # delete Venue
        self.venue.delete()

        super(Performance, self).delete()

    def get_cms_data(self):
        start_on = isodate.datetime_isoformat(self.start_on) if self.start_on else ''
        end_on = isodate.datetime_isoformat(self.end_on) if self.end_on else ''
        open_on = isodate.datetime_isoformat(self.open_on) if self.open_on else ''

        # 削除されたデータも集める
        sales_segments = DBSession.query(SalesSegment, include_deleted=True).filter_by(performance_id=self.id).all()

        # cmsでは日付は必須項目
        if not start_on and not self.deleted_at:
            raise Exception(u'パフォーマンスの日付を入力してください')

        data = {
            'id':self.id,
            'name':self.name,
            'venue':(self.venue.name if self.venue else ''),
            'prefecture':(self.venue.site.prefecture if self.venue and self.venue.site else ''),
            'open_on':open_on,
            'start_on':start_on,
            'end_on':end_on,
            "code": self.code or "", 
            'sales':[s.get_cms_data() for s in sales_segments],
            'public':self.public
        }
        if self.deleted_at:
            data['deleted'] = 'true'

        return data

    def query_sales_segments(self, user=None, now=None, type='available'):
        """ISalesSegmentQueryable.query_sales_segments)"""
        q = build_sales_segment_query(performance_id=self.id, user=user, now=now, type=type)
        return q

    @classmethod
    def get(cls, id, organization_id=None, **kwargs):
        if organization_id:
            return Performance.filter(Performance.id==id).join(Event).filter(Event.organization_id==organization_id).first()
        return super(Performance, cls).get(id, **kwargs)

    @staticmethod
    def create_from_template(template, **kwargs):
        logger.info('[copy] Performance start')
        performance = Performance.clone(template)
        if 'event_id' in kwargs:
            event = Event.get(kwargs['event_id'])
            performance.event_id = event.id
            performance.code = event.code + performance.code[5:]
        performance.original_id = template.id
        performance.venue_id = template.venue.id
        performance.create_venue_id = template.venue.id       
        performance.save()
        logger.info('[copy] Performance end')

    def has_that_delivery(self, delivery_plugin_id):
        qs = DBSession.query(DeliveryMethod)\
            .filter(DeliveryMethod.delivery_plugin_id==delivery_plugin_id)\
            .filter(DeliveryMethod.id==PaymentDeliveryMethodPair.delivery_method_id)\
            .filter(PaymentDeliveryMethodPair.sales_segment_group_id == SalesSegment.id)\
            .filter(SalesSegment.id==Product.sales_segment_group_id)\
            .filter(Product.id==ProductItem.product_id)\
            .filter(ProductItem.performance_id==self.id)
        return bool(qs.first())

class ReportFrequencyEnum(StandardEnum):
    Daily = (1, u'毎日')
    Weekly = (2, u'毎週')

class ReportPeriodEnum(StandardEnum):
    Normal = (1, u'指定期間 (前日分/前週分)')
    Entire = (2, u'全期間 (販売開始〜送信日時まで)')

class ReportSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = 'ReportSetting'
    id = Column(Identifier, primary_key=True)
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'), nullable=True)
    event = relationship('Event', backref='report_settings')
    performance_id = Column(Identifier, ForeignKey('Performance.id', ondelete='CASCADE'), nullable=True)
    performance = relationship('Performance', backref='report_settings')
    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), nullable=True)
    operator = relationship('Operator', backref='report_setting')
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    frequency = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    time = Column(String(4), nullable=False)
    day_of_week = Column(Integer, nullable=True, default=None)
    start_on = Column(DateTime, nullable=True, default=None)
    end_on = Column(DateTime, nullable=True, default=None)

    @property
    def recipient(self):
        if self.operator:
            return self.operator.email
        else:
            return self.email

def build_sales_segment_query(event_id=None, performance_id=None, sales_segment_group_id=None, sales_segment_id=None, user=None, now=None, type='available'):
    if all(not x for x in [event_id, performance_id, sales_segment_group_id, sales_segment_id]):
        raise ValueError("any of event_id, performance_id, sales_segment_group_id or sales_segment_id must be non-null value")

    q = SalesSegment.query
    q = q.options(
        joinedload(
            SalesSegment.sales_segment_group,
            SalesSegmentGroup.membergroups))
    q = q.filter(SalesSegment.public != False)
    q = q.filter(SalesSegmentGroup.public != False)
    q = q.filter(SalesSegmentGroup.normal_sales | SalesSegmentGroup.sales_counter) # XXX: 窓口販売が当日券用の区分に使われている。このようなケースでは、publicフラグがTrueであることを必ずチェックしなければならない

    if event_id is not None:
        q = q.filter(Performance.event_id == event_id)
        q = q.filter(SalesSegmentGroup.event_id == event_id)
    if performance_id is not None:
        q = q.filter(Performance.id == performance_id)
        q = q.filter(Event.id == Performance.event_id)
        q = q.filter(SalesSegmentGroup.event_id == Event.id)
    if sales_segment_group_id is not None:
        q = q.filter(SalesSegmentGroup.id == sales_segment_group_id)
    if sales_segment_id is not None:
        q = q.filter(SalesSegment.id == sales_segment_id)

    q = q.filter(Performance.id==SalesSegment.performance_id)
    q = q.filter(Performance.public != False)
    q = q.filter(SalesSegment.sales_segment_group_id==SalesSegmentGroup.id)

    if type == 'available':
        q = q.filter(SalesSegment.in_term(now))
    elif type == 'from':
        q = q.filter(SalesSegment.start_at >= now)
    elif type == 'before':
        q = q.filter(SalesSegment.end_at < now)

    if user and user.get('is_guest'):
        q = q \
            .outerjoin(MemberGroup,
                       SalesSegmentGroup.membergroups) \
            .filter(or_(MemberGroup.is_guest != False,
                        MemberGroup.id == None))
    elif user and 'membership' in user:
        q = q \
            .outerjoin(MemberGroup,
                       SalesSegmentGroup.membergroups) \
            .filter(
                or_(
                    or_(MemberGroup.is_guest != False,
                        MemberGroup.id == None),
                    MemberGroup.name == user['membergroup']
                    )
                )
    return q

@implementer(ISalesSegmentQueryable)
class Event(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Event'

    id = Column(Identifier, primary_key=True)
    code = Column(String(12))  # Organization.code(2桁) + 3桁英数字大文字のみ
    title = AnnotatedColumn(String(1024), _a_label=(u'名称'))
    abbreviated_title = AnnotatedColumn(String(1024), _a_label=(u'略称'))

    account_id = AnnotatedColumn(Identifier, ForeignKey('Account.id'), _a_label=(u'配券元'))
    account = relationship('Account', backref='events')

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='events')

    performances = relationship('Performance', backref='event', order_by='Performance.start_on')
    stock_types = relationship('StockType', backref='event', order_by='StockType.display_order')
    stock_holders = relationship('StockHolder', backref='event')

    sales_segment_groups = relationship('SalesSegmentGroup')
    cms_send_at = Column(DateTime, nullable=True, default=None)

    _first_performance = None
    _final_performance = None

    @property
    def accounts(self):
        return Account.filter().join(Account.stock_holders).filter(StockHolder.event_id==self.id).all()

    @property
    def sales_start_on(self):
        return SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id==self.id)\
                .join(SalesSegment)\
                .join(Product).filter(Product.sales_segment_id==SalesSegment.id)\
                .with_entities(func.min(SalesSegment.start_at)).scalar()

    @property
    def sales_end_on(self):
        return SalesSegmentGroup.query.filter(SalesSegmentGroup.event_id==self.id)\
                .join(SalesSegment)\
                .join(Product).filter(Product.sales_segment_id==SalesSegment.id)\
                .with_entities(func.max(SalesSegment.end_at)).scalar()

    @property
    def first_start_on(self):
        return self.first_performance.start_on if self.first_performance else ''

    @property
    def final_start_on(self):
        return self.final_performance.start_on if self.final_performance else ''

    @property
    def first_performance(self):
        if not self._first_performance:
            self._first_performance = Performance.filter(Performance.event_id==self.id)\
                                        .filter(Performance.start_on!=None)\
                                        .order_by('Performance.start_on asc').first()
        return self._first_performance

    @property
    def final_performance(self):
        if not self._final_performance:
            self._final_performance = Performance.filter(Performance.event_id==self.id)\
                                        .filter(Performance.start_on!=None)\
                                        .order_by('Performance.start_on desc').first()
        return self._final_performance

    @staticmethod
    def get_owner_event(account):
        return Event.query.join(Event.account).filter(Account.id==account.id).all()

    @staticmethod
    def get_client_event(account):
        return Event.query.filter(Event.organization_id==account.organization_id)\
                          .join(Event.stock_holders)\
                          .join(StockHolder.account)\
                          .filter(Account.id==account.id)\
                          .all()

    def _get_self_cms_data(self):
        return {'id':self.id,
                'title':self.title,
                'code': self.code, 
                'subtitle':self.abbreviated_title,
                "organization_id": self.organization.id, 
                }

    def get_cms_data(self, validation=True):
        '''
        CMSに連携するデータを生成する
        インターフェースのデータ構造は以下のとおり
        削除データには "deleted":"true" をいれる
        
        see:ticketing.core.tests_event_notify_data.py
        '''
        # 論理削除レコードも含めて取得
        performances = DBSession.query(Performance, include_deleted=True).filter_by(event_id=self.id).all()
        data = self._get_self_cms_data()
        data.update({
            'performances':[p.get_cms_data() for p in performances],
        })
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    def add(self):
        super(Event, self).add()

        if hasattr(self, 'original_id') and self.original_id:
            """
            Eventのコピー時は以下のモデルをcloneする
              - StockType
              - StockHolder
              - SalesSegmentGroup
                − MemberGroup_SalesSegment
                - PaymentDeliveryMethodPair
              - TicketBundle
                - Ticket_TicketBundle
                - TicketBundleAttribute
                - Ticket
              - Performance
                - (この階層以下はPerformance.add()を参照)
            """
            template_event = Event.get(self.original_id)

            # 各モデルのコピー元/コピー先のidの対比表
            convert_map = {
                'stock_type':dict(),
                'stock_holder':dict(),
                'sales_segment_group':dict(),
                'product':dict(),
                'ticket':dict(),
                'ticket_bundle':dict(),
            }

            # create StockType
            for template_stock_type in template_event.stock_types:
                convert_map['stock_type'].update(
                    StockType.create_from_template(template=template_stock_type, event_id=self.id)
                )

            # create StockHolder
            for template_stock_holder in template_event.stock_holders:
                convert_map['stock_holder'].update(
                    StockHolder.create_from_template(template=template_stock_holder, event_id=self.id)
                )

            # create SalesSegmentGroup
            for template_sales_segment_group in template_event.sales_segment_groups:
                convert_map['sales_segment_group'].update(
                    SalesSegmentGroup.create_from_template(template=template_sales_segment_group, with_payment_delivery_method_pairs=True, event_id=self.id)
                )

            # create Ticket
            for template_ticket in template_event.tickets:
                convert_map['ticket'].update(
                    Ticket.create_from_template(template=template_ticket, event_id=self.id)
                )

            # create TicketBundle
            for template_ticket_bundle in template_event.ticket_bundles:
                convert_map['ticket_bundle'].update(
                    TicketBundle.create_from_template(template=template_ticket_bundle, event_id=self.id, **convert_map)
                )

            # create Performance
            for template_performance in template_event.performances:
                Performance.create_from_template(template=template_performance, event_id=self.id)

            convert_map['payment_delivery_method_pair'] = {}
            for org_id, new_id in convert_map['sales_segment_group'].iteritems():
                ssg = SalesSegmentGroup.get(org_id)
                for org_pdmp in ssg.payment_delivery_method_pairs:
                    new_pdmp = PaymentDeliveryMethodPair.query.filter(and_(
                        PaymentDeliveryMethodPair.sales_segment_group_id==new_id,
                        PaymentDeliveryMethodPair.payment_method_id==org_pdmp.payment_method_id,
                        PaymentDeliveryMethodPair.delivery_method_id==org_pdmp.delivery_method_id
                    )).first()
                    convert_map['payment_delivery_method_pair'][org_pdmp.id] = new_pdmp.id

            '''
            Performance以下のコピーしたモデルにidを反映する
            '''
            performances = Performance.filter_by(event_id=self.id).with_entities(Performance.id).all()
            for performance in performances:
                # 関連テーブルのstock_type_idを書き換える
                for old_id, new_id in convert_map['stock_type'].iteritems():
                    Stock.query.filter(and_(Stock.stock_type_id==old_id, Stock.performance_id==performance.id)).update({'stock_type_id':new_id})
                    Product.query.filter(and_(Product.seat_stock_type_id==old_id, Product.performance_id==performance.id)).update({'seat_stock_type_id':new_id})

                # 関連テーブルのsales_holder_idを書き換える
                for old_id, new_id in convert_map['stock_holder'].iteritems():
                    Stock.query.filter(and_(Stock.stock_holder_id==old_id, Stock.performance_id==performance.id)).update({'stock_holder_id':new_id})

                # 関連テーブルのsales_segment_group_idを書き換える
                for old_id, new_id in convert_map['sales_segment_group'].iteritems():
                    sales_segments = SalesSegment.query.filter(and_(SalesSegment.sales_segment_group_id==old_id, SalesSegment.performance_id==performance.id)).all()
                    for sales_segment in sales_segments:
                        sales_segment.sales_segment_group_id = new_id
                        new_pdmps = []
                        for old_pdmp in sales_segment.payment_delivery_method_pairs:
                            id = convert_map['payment_delivery_method_pair'][old_pdmp.id]
                            new_pdmp = PaymentDeliveryMethodPair.get(id)
                            if new_pdmp:
                                new_pdmps.append(new_pdmp)
                        sales_segment.payment_delivery_method_pairs = list()
                        for new_pdmp in new_pdmps:
                            sales_segment.payment_delivery_method_pairs.append(new_pdmp)

                # 関連テーブルのticket_bundle_idを書き換える
                for old_id, new_id in convert_map['ticket_bundle'].iteritems():
                    ProductItem.query.filter(and_(ProductItem.ticket_bundle_id==old_id, ProductItem.performance_id==performance.id)).update({'ticket_bundle_id':new_id})
        else:
            """
            Eventの作成時は以下のモデルを自動生成する
              - Account (自社枠、ない場合のみ)
                - StockHolder (デフォルト枠)
            """
            account = Account.filter_by(organization_id=self.organization.id)\
                             .filter_by(user_id=self.organization.user_id).first()
            if not account:
                account = Account(
                    account_type=AccountTypeEnum.Playguide.v[0],
                    name=u'自社',
                    user_id=self.organization.user_id,
                    organization_id=self.organization.id,
                )
                account.save()
            StockHolder.create_default(event_id=self.id, account_id=account.id)

    def delete(self):
        # delete Performance
        for performance in self.performances:
            performance.delete()

        # delete SalesSegmentGroup
        for sales_segment_group in self.sales_segment_groups:
            sales_segment_group.delete()

        # delete StockType
        for stock_type in self.stock_types:
            stock_type.delete()

        # delete StockHolder
        for stock_holder in self.stock_holders:
            stock_holder.delete()

        # delete Product
        for product in self.products:
            product.delete()

        super(Event, self).delete()

    def query_available_sales_segments(self, user=None, now=None):
        return self.query_sales_segments(user=user, now=now, type='available')

    def query_sales_segments(self, user=None, now=None, type='available'):
        q = build_sales_segment_query(event_id=self.id, user=user, now=now, type=type)
        return q

    @staticmethod
    def find_next_and_last_sales_segment_period(sales_segments, now):
        per_performance_data = {}
        next_sales_segment = None
        last_sales_segment = None

        for sales_segment in sales_segments:
            # 直近の販売区分を調べる
            if sales_segment.start_at >= now and (next_sales_segment is None or next_sales_segment.start_at > sales_segment.start_at):
                next_sales_segment = sales_segment
            if sales_segment.end_at is not None and sales_segment.end_at < now and (last_sales_segment is None or last_sales_segment.end_at < sales_segment.end_at):
                last_sales_segment = sales_segment
            # のと同時に、パフォーマンス毎の販売区分のリストをつくる
            per_performance_datum = per_performance_data.get(sales_segment.performance_id)
            if per_performance_datum is None:
                per_performance_datum = per_performance_data[sales_segment.performance_id] = dict(
                    performance=sales_segment.performance,
                    sales_segment=None,
                    sales_segments=[sales_segment],
                    start_at=sales_segment.start_at,
                    end_at=sales_segment.end_at
                    )
            else:
                per_performance_datum['sales_segments'].append(sales_segment)
                if per_performance_datum['start_at'] > sales_segment.start_at:
                    per_performance_datum['start_at'] = sales_segment.start_at
                if per_performance_datum['end_at'] < sales_segment.end_at:
                    per_performance_datum['end_at'] = sales_segment.end_at

        # まずは個々のパフォーマンスについて、そのパフォーマンスの全販売区分を
        # 含む期間の先頭と末尾が現在日時と被らないものを探す
        next = None
        last = None
        for per_performance_datum in per_performance_data.itervalues():
            if per_performance_datum['start_at'] >= now:
                if next is None or per_performance_datum['start_at'] < next['start_at']:
                    next = per_performance_datum
            elif per_performance_datum['end_at'] is not None and per_performance_datum['end_at'] < now:
                if last is None or per_performance_datum['end_at'] > last['end_at']:
                    last = per_performance_datum

        # もしそのようなパフォーマンスが見つからないときは、販売区分と販売区分の
        # ちょうど合間であると考えられるので、販売区分をもとに戻り値を構築する
        if not next and not last:
            return tuple(sales_segment and \
                            dict(sales_segment=sales_segment,
                                sales_segment_name=sales_segment.name,
                                performance=sales_segment.performance,
                                sales_segments=None,
                                start_at=sales_segment.start_at,
                                end_at=sales_segment.end_at) \
                         for sales_segment in (next_sales_segment, last_sales_segment))
        else:
            return next, last

    def get_next_and_last_sales_segment_period(self, user=None, now=None):
        now = now or datetime.now()
        return self.find_next_and_last_sales_segment_period(
            self.query_sales_segments(user=user, now=now, type='all'),
            now)

class SalesSegmentKindEnum(StandardEnum):
    normal          = u'一般発売'
    same_day        = u'当日券'
    early_firstcome = u'先行先着'
    added_sales     = u'追加発売'
    early_lottery   = u'先行抽選'
    added_lottery   = u'追加抽選'
    first_lottery   = u'最速抽選'
    vip             = u'関係者'
    sales_counter   = u'窓口販売'
    other           = u'その他'
    order = [
        'normal',
        'same_day',
        'early_firstcome',
        'added_sales',
        'early_lottery',
        'added_lottery',
        'first_lottery',
        'vip',
        'sales_counter',
        'other',
    ]

@implementer(ISalesSegmentQueryable)
class SalesSegmentGroup(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SalesSegmentGroup'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    name = AnnotatedColumn(String(255), _a_label=_(u'名前'))
    kind = AnnotatedColumn(String(255), _a_label=_(u'種別'))
    start_at = AnnotatedColumn(DateTime, _a_label=_(u'販売開始日時'))
    end_at = AnnotatedColumn(DateTime, _a_label=_(u'販売終了日時'))
    upper_limit = AnnotatedColumn(Integer, _a_label=_(u'購入上限枚数'))
    order_limit = AnnotatedColumn(Integer, _a_label=_(u'購入回数制限'))

    seat_choice = AnnotatedColumn(Boolean, default=True, _a_label=_(u'座席選択可'))
    public = AnnotatedColumn(Boolean, default=True, _a_label=_(u'一般公開'))
    reporting = AnnotatedColumn(Boolean, nullable=False, default=True, server_default='1', _a_label=_(u'レポート対象'))

    margin_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=_(u'販売手数料率(%)'))
    refund_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=_(u'払戻手数料率(%)'))
    printing_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=_(u'印刷代金(円/枚)'))
    registration_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=_(u'登録手数料(円/公演)'))
    account_id = AnnotatedColumn(Identifier, ForeignKey('Account.id'), _a_label=_(u'配券元'))
    account = relationship('Account', backref='sales_segment_groups')

    event_id = AnnotatedColumn(Identifier, ForeignKey('Event.id'), _a_label=_(u'イベント'))
    event = relationship('Event')
    auth3d_notice = Column(UnicodeText)

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref="sales_segment_group")

    start_day_prior_to_performance = Column(Integer)
    start_time = Column(Time)
    end_day_prior_to_performance = Column(Integer)
    end_time = Column(Time)

    @hybrid_method
    def in_term(self, dt):
        return (self.start_at <= dt) and ((self.end_at is None) or (dt <= self.end_at))

    @in_term.expression
    def in_term_expr(self, dt):
        return (self.start_at <= dt) & ((None == self.end_at) | (dt <= self.end_at))

    @classmethod
    def get(cls, id, organization_id=None, **kwargs):
        if organization_id:
            return cls.query.filter(cls.id==id).join(Event).filter(Event.organization_id==organization_id).first()
        return super(cls, cls).get(id, **kwargs)

    def delete(self):
        # delete SalesSegment
        for sales_segment in self.sales_segments:
            sales_segment.delete()

        # delete Product
        for product in self.product:
            product.delete()

        # delete PaymentDeliveryMethodPair
        for pdmp in self.payment_delivery_method_pairs:
            pdmp.delete()

        super(type(self), self).delete()

    def new_sales_segment(self):
        return SalesSegment(sales_segment_group=self,
                            event=self.event,
                            organization=self.organization,
                            membergroups=[m for m in self.membergroups])

    @staticmethod
    def create_from_template(template, with_payment_delivery_method_pairs=False, **kwargs):
        sales_segment_group = SalesSegmentGroup.clone(template)
        if 'event_id' in kwargs:
            sales_segment_group.event_id = kwargs['event_id']
        sales_segment_group.membergroups = template.membergroups
        sales_segment_group.save()

        if with_payment_delivery_method_pairs:
            for template_pdmp in template.payment_delivery_method_pairs:
                PaymentDeliveryMethodPair.create_from_template(template=template_pdmp, sales_segment_group_id=sales_segment_group.id, **kwargs)

        return {template.id:sales_segment_group.id}

    def get_products(self, performances):
        """ この販売区分で購入可能な商品一覧 """
        return [product for product in self.product if product.performances in performances]

    @hybrid_property
    def lot(self):
        return is_any_of(
            self.kind,
            (
                SalesSegmentKindEnum.first_lottery.k,
                SalesSegmentKindEnum.early_lottery.k,
                SalesSegmentKindEnum.added_lottery.k)
            )

    @hybrid_property
    def sales_counter(self):
        return self.kind == SalesSegmentKindEnum.sales_counter.k

    @hybrid_property
    def normal_sales(self):
        return is_any_of(
            self.kind,
            (
                SalesSegmentKindEnum.early_firstcome.k,
                SalesSegmentKindEnum.normal.k,
                SalesSegmentKindEnum.added_sales.k)
            )

    @property
    def has_guest(self):
        return (not self.membergroups) or any(mg.is_guest for mg in self.membergroups)

    # 4423対応中の緩衝材メソッド
    def sync_member_group_to_children(self):
        for ss in self.sales_segments:
            ss.membergroups = [mg for mg in self.membergroups]
            ss.event = self.event
            ss.organization = self.organization

    def start_for_performance(self, performance):
        """ 公演開始日に対応した販売開始日時を算出
        start_atによる直接指定の場合は、start_atを利用する
        """

        if self.start_at:
            return self.start_at

        s = performance.start_on
        d = datetime(s.year, s.month, s.day,
                     self.start_time.hour, self.start_time.minute)
        d -= timedelta(days=self.start_day_prior_to_performance)
        return d

    def end_for_performance(self, performance):
        """ 公演開始日に対応した販売終了日時を算出
        end_atによる直接指定の場合は、end_atを利用する
        """
        if self.end_at:
            return self.end_at

        s = performance.start_on
        d = datetime(s.year, s.month, s.day,
                     self.end_time.hour, self.end_time.minute)
        d -= timedelta(days=self.end_day_prior_to_performance)
        return d

    def query_sales_segments(self, user=None, now=None, type='available'):
        """ISalesSegmentQueryable.query_sales_segments)"""
        q = build_sales_segment_query(sales_segment_group_id=self.id, user=user, now=now, type=type)
        return q

SalesSegment_PaymentDeliveryMethodPair = Table(
    "SalesSegment_PaymentDeliveryMethodPair",
    Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('payment_delivery_method_pair_id', Identifier, ForeignKey('PaymentDeliveryMethodPair.id')),
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    )

class PaymentDeliveryMethodPair(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentDeliveryMethodPair'
    query = DBSession.query_property()
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))

    system_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'システム利用料'))
    system_fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])
    
    transaction_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'決済手数料'))
    delivery_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'引取手数料'))
    discount = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'割引額'))
    discount_unit = AnnotatedColumn(Integer, _a_label=_(u'割引数'))

    # 申込日から計算して入金できる期限、日数指定
    payment_period_days = Column(Integer, default=3)
    # 入金から発券できるまでの時間
    issuing_interval_days = Column(Integer, default=1)
    issuing_start_at = Column(DateTime, nullable=True)
    issuing_end_at = Column(DateTime, nullable=True)
    # 選択不可期間 (SalesSegment.start_atの何日前から利用できないか、日数指定)
    unavailable_period_days = AnnotatedColumn(Integer, nullable=False, default=0, _a_label=_(u'選択不可期間'))
    # 一般公開するか
    public = AnnotatedColumn(Boolean, nullable=False, default=True, _a_label=_(u'一般公開'))

    sales_segment_group_id = AnnotatedColumn(Identifier, ForeignKey('SalesSegmentGroup.id'), _a_label=_(u'販売区分グループ'))
    sales_segment_group = relationship('SalesSegmentGroup', backref='payment_delivery_method_pairs')
    payment_method_id = AnnotatedColumn(Identifier, ForeignKey('PaymentMethod.id'), _a_label=_(u'決済方法'))
    payment_method = relationship('PaymentMethod', backref='payment_delivery_method_pairs')
    delivery_method_id = AnnotatedColumn(Identifier, ForeignKey('DeliveryMethod.id'), _a_label=_(u'引取方法'))
    delivery_method = relationship('DeliveryMethod', backref='payment_delivery_method_pairs')

    special_fee_name = AnnotatedColumn(String(255), nullable=False, _a_label=_(u'特別手数料名'), default="")
    special_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False,
                                  _a_label=_(u'特別手数料'), default=FeeTypeEnum.Once.v[0])
    special_fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])

    @property
    def delivery_fee_per_product(self):
        """商品ごとの引取手数料"""
        return Decimal()

    @property
    def delivery_fee_per_ticket(self):
        """発券ごとの引取手数料"""
        if self.delivery_method.fee_type == FeeTypeEnum.PerUnit.v[0]:
            return self.delivery_fee
        else:
            return Decimal()

    @property
    def delivery_fee_per_order(self):
        """注文ごとの引取手数料"""
        if self.delivery_method.fee_type == FeeTypeEnum.Once.v[0]:
            return self.delivery_fee
        else:
            return Decimal()

    @property
    def transaction_fee_per_product(self):
        """商品ごとの決済手数料"""
        return Decimal()

    @property
    def transaction_fee_per_ticket(self):
        """発券ごとの決済手数料"""
        if self.payment_method.fee_type == FeeTypeEnum.PerUnit.v[0]:
            return self.transaction_fee
        else:
            return Decimal()

    @property
    def transaction_fee_per_order(self):
        """注文ごとの決済手数料"""
        if self.payment_method.fee_type == FeeTypeEnum.Once.v[0]:
            return self.transaction_fee
        else:
            return Decimal()

    @property
    def system_fee_per_product(self):
        """商品ごとのシステム利用料"""
        return Decimal()

    @property
    def system_fee_per_ticket(self):
        """発券ごとのシステム利用料"""
        if self.system_fee_type == FeeTypeEnum.PerUnit.v[0]:
            return self.system_fee
        else:
            return Decimal()

    @property
    def system_fee_per_order(self):
        """注文ごとのシステム利用料"""
        if self.system_fee_type == FeeTypeEnum.Once.v[0]:
            return self.system_fee
        else:
            return Decimal()

    @property
    def special_fee_per_product(self):
        """商品ごとの特別手数料"""
        return Decimal()

    @property
    def special_fee_per_ticket(self):
        """発券ごとの特別手数料"""
        if self.special_fee_type == FeeTypeEnum.PerUnit.v[0]:
            return self.special_fee
        else:
            return Decimal()

    @property
    def special_fee_per_order(self):
        """注文ごとの特別手数料"""
        if self.special_fee_type == FeeTypeEnum.Once.v[0]:
            return self.special_fee
        else:
            return Decimal()

    @property
    def per_order_fee(self):
        """注文ごと手数料"""
        return self.system_fee_per_order + self.special_fee_per_order + self.delivery_fee_per_order + self.transaction_fee_per_order

    @property
    def per_product_fee(self):
        return self.system_fee_per_product + self.special_fee_per_product + self.delivery_fee_per_product + self.transaction_fee_per_product
    
    @property
    def per_ticket_fee(self):
        return self.system_fee_per_ticket + self.special_fee_per_ticket + self.delivery_fee_per_ticket + self.transaction_fee_per_ticket

    def is_available_for(self, sales_segment, on_day):
        return self.public and (
            sales_segment.end_at is None or \
            (todate(on_day) <= (sales_segment.end_at.date()
                                - timedelta(days=self.unavailable_period_days)))
            )

    @staticmethod
    def create_from_template(template, **kwargs):
        pdmp = PaymentDeliveryMethodPair.clone(template)
        if 'sales_segment_group_id' in kwargs:
            pdmp.sales_segment_group_id = kwargs['sales_segment_group_id']
        pdmp.save()

    def delete(self):
        # 既に予約がある場合は削除できない
        if self.orders:
            raise Exception(u'予約がある為、削除できません')
        # 既に抽選申込がある場合は削除できない
        if self.lot_entries:
            raise Exception(u'抽選申込がある為、削除できません')
        super(PaymentDeliveryMethodPair, self).delete()

class PaymentMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))


class ServiceFeeMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ServiceFeeMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(2000))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='service_fee_method_list') 
    system_fee_default = Column(Boolean, nullable=False, default=True)

    @property
    def fee_type_label(self):
        for ft in FeeTypeEnum:
            if ft.v[0] == self.fee_type:
                return ft.v[1]
    
class PaymentMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(2000))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])
    public = Column(Boolean, nullable=False, default=True)

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(Identifier, ForeignKey('PaymentMethodPlugin.id'))

    # 払込票を表示しないオプション（SEJ専用）
    hide_voucher = Column(Boolean, default=False)
    
    _payment_plugin = relationship('PaymentMethodPlugin', uselist=False)
    @hybrid_property
    def payment_plugin(self):
        warn_deprecated("deprecated attribute `payment_plugin' is accessed")
        return self._payment_plugin

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.payment_delivery_method_pairs:
            raise Exception(u'関連づけされた決済・引取方法がある為、削除できません')

        super(PaymentMethod, self).delete()

    @property
    def fee_type_label(self):
        for ft in FeeTypeEnum:
            if ft.v[0] == self.fee_type:
                return ft.v[1]

    @staticmethod
    def filter_by_organization_id(id):
        return PaymentMethod.filter(PaymentMethod.organization_id==id).all()

class DeliveryMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(2000))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')

    
    delivery_plugin_id = Column(Identifier, ForeignKey('DeliveryMethodPlugin.id'))
    _delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)


    # 引換票を表示しないオプション（SEJ専用）
    hide_voucher = Column(Boolean, default=False)

    @hybrid_property
    def delivery_plugin(self):
        warn_deprecated("deprecated attribute `delivery_plugin' is accessed")
        return self._delivery_plugin

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.payment_delivery_method_pairs:
            raise Exception(u'関連づけされた決済・引取方法がある為、削除できません')

        super(DeliveryMethod, self).delete()

    @property
    def fee_type_label(self):
        for ft in FeeTypeEnum:
            if ft.v[0] == self.fee_type:
                return ft.v[1]

    @staticmethod
    def filter_by_organization_id(id):
        return DeliveryMethod.filter(DeliveryMethod.organization_id==id).all()

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('buyer_condition_id', Identifier, ForeignKey('BuyerCondition.id')),
    Column('product_id', Identifier, ForeignKey('Product.id'))
)

class BuyerCondition(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'BuyerCondition'
    id = Column(Identifier, primary_key=True)

    member_ship_id = Column(Identifier, ForeignKey('Membership.id'))
    member_ship   = relationship('Membership')
    '''
     Any Conditions.....
    '''

class ProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ProductItem'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    product_id = Column(Identifier, ForeignKey('Product.id'))
    performance_id = Column(Identifier, ForeignKey('Performance.id'))

    stock_id = Column(Identifier, ForeignKey('Stock.id'))
    stock = relationship("Stock", backref="product_items")

    quantity = Column(Integer, nullable=False, default=1, server_default='1')
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id'), nullable=True)

    @property
    def stock_type_id(self):
        return self.stock.stock_type_id

    @property
    def stock_type(self):
        return self.stock.stock_type

    def get_for_update(self):
        self.stock = Stock.get_for_update(self.performance_id, self.stock_type_id)
        if self.stock != None:
            self.seatStatus = SeatStatus.get_for_update(self.stock.id)
            return self.seatStatus
        else:
            return None

    def delete(self):
        # 既に予約されている場合は削除できない
        if self.ordered_product_items:
            raise Exception(u'予約がある為、削除できません')

        super(ProductItem, self).delete()

    @staticmethod
    def create_default(product):
        '''
        ProductIetmを自動生成する
          - Productが座席(StockType.is_seatが真)をもっていること
          - Product追加時に、Performance * StockHolderの数分生成
          - Stock追加時に、該当StockTypeのProductに対して、Performance * StockHolderの数分生成
            * Stock追加 ＝ StockType or StockHolder or Performance のいずれかが追加されたとき
        '''
        for performance in product.event.performances:
            product_item = [item for item in product.items if item.performance_id == performance.id]
            if not product_item:
                # デフォルト(自社)のStockHolderに紐づける
                stock_holders = StockHolder.get_own_stock_holders(event=performance.event)
                stock = Stock.filter_by(performance_id=performance.id)\
                             .filter_by(stock_type_id=product.seat_stock_type_id)\
                             .filter_by(stock_holder_id=stock_holders[0].id)\
                             .first()
                product_item = ProductItem(
                    price=product.price,
                    product_id=product.id,
                    performance_id=performance.id,
                    stock_id=stock.id,
                )
                product_item.save()

    @staticmethod
    def create_from_template(template, **kwargs):
        if not template.product.performance:
            # Product.performance_idがないレコードはSalesSegmentGroup追加時の移行用なのでコピーしない
            return
        if not template.product.sales_segment.performance:
            # SalesSegment.performance_idがないレコードは抽選用なのでコピーしない
            return
        product_item = ProductItem.clone(template)
        if 'performance_id' in kwargs:
            product_item.performance_id = kwargs['performance_id']
        if 'product_id' in kwargs:
            product_item.product_id = kwargs['product_id']
            product = Product.query.filter_by(id=kwargs['product_id']).first()
            product_item.performance_id = product.performance_id
        if 'stock_id' in kwargs:
            product_item.stock_id = kwargs['stock_id']
        else:
            conditions = dict(
                performance_id=product_item.performance_id,
                stock_holder_id=template.stock.stock_holder_id,
                stock_type_id=template.stock.stock_type_id
            )
            if 'stock_holder_id' in kwargs and kwargs['stock_holder_id']:
                conditions['stock_holder_id'] = kwargs['stock_holder_id']
            stock = Stock.filter_by(**conditions).first()
            product_item.stock = stock
        product_item.save()

class StockTypeEnum(StandardEnum):
    Seat = 0
    Other = 1

class StockType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'StockType'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    type = Column(Integer)  # @see StockTypeEnum
    display = Column(Boolean, default=True)
    display_order = Column(Integer, nullable=False, default=1)
    event_id = Column(Identifier, ForeignKey("Event.id"))
    quantity_only = Column(Boolean, default=False)
    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))
    description=Column(Unicode(2000), nullable=True, default=None)
    stocks = relationship('Stock', backref=backref('stock_type', order_by='StockType.display_order'))

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

    def add(self):
        super(StockType, self).add()

        # create default Stock
        Stock.create_default(self.event, stock_type_id=self.id)

    def delete(self):
        # delete Stock
        for stock in self.stocks:
            stock.delete()

        # delete Product
        products = Product.filter_by(event_id=self.event_id).filter_by(seat_stock_type_id=self.id).all()
        for product in products:
            product.delete()

        super(StockType, self).delete()

    def num_seats(self, performance_id=None, sale_only=False):
        # 同一Performanceの同一StockTypeにおけるStock.quantityの合計
        query = Stock.filter_by(stock_type_id=self.id).with_entities(func.sum(Stock.quantity))
        if performance_id:
            query = query.filter_by(performance_id=performance_id)
            if sale_only:
                query = query.filter(exists().where(and_(ProductItem.performance_id==performance_id, ProductItem.stock_id==Stock.id)))
        return query.scalar()

    def rest_num_seats(self, performance_id=None, sale_only=False):
        # 同一Performanceの同一StockTypeにおけるStockStatus.quantityの合計
        query = Stock.filter(Stock.stock_type_id==self.id).join(Stock.stock_status).with_entities(func.sum(StockStatus.quantity))
        if performance_id:
            query = query.filter(Stock.performance_id==performance_id)
            if sale_only:
                query = query.filter(exists().where(and_(ProductItem.performance_id==performance_id, ProductItem.stock_id==Stock.id)))
        return query.scalar()

    def set_style(self, data):
        if self.is_seat:
            self.style = {
                'stroke':{
                    'color':data.get('stroke_color'),
                    'width':data.get('stroke_width'),
                    'pattern':data.get('stroke_patten'),
                },
                'fill':{
                    'color':data.get('fill_color'),
                },
            }
        else:
            self.style = {}

    @staticmethod
    def create_from_template(template, **kwargs):
        stock_type = StockType.clone(template)
        if 'event_id' in kwargs:
            stock_type.event_id = kwargs['event_id']
        stock_type.save()
        return {template.id:stock_type.id}

class StockHolder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockHolder"
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

    event_id = Column(Identifier, ForeignKey('Event.id'))
    account_id = Column(Identifier, ForeignKey('Account.id'))

    style = deferred(Column(MutationDict.as_mutable(JSONEncodedDict(1024))))
    stocks = relationship('Stock', backref='stock_holder')

    def add(self):
        super(StockHolder, self).add()

        # create default Stock
        Stock.create_default(self.event, stock_holder_id=self.id)

    def delete(self):
        # delete Stock
        for stock in self.stocks:
            stock.delete()

        super(StockHolder, self).delete()

    def stocks_by_performance(self, performance_id):
        def performance_filter(stock):
            return (stock.performance_id == performance_id)
        return filter(performance_filter, self.stocks)

    @staticmethod
    def get_own_stock_holders(event=None, user_id=None):
        query = StockHolder.query.join(Account)
        if event is not None:
            query = query.filter(StockHolder.event_id==event.id)
            user_id = event.organization.user_id
        query = query.filter(Account.user_id==user_id)
        return query.order_by('StockHolder.id').all()

    @staticmethod
    def create_default(event_id, account_id):
        defaults = [
            dict(name=u'自社', style={"text": u"自", "text_color": "#a62020"}),
            dict(name=u'追券枠', style={"text": u"追", "text_color": "#a62020"}),
            dict(name=u'返券枠', style={"text": u"返", "text_color": "#a62020"}),
        ]
        for sh in defaults:
            stock_holder = StockHolder(name=sh['name'], event_id=event_id, account_id=account_id, style=sh['style'])
            stock_holder.save()

    @staticmethod
    def create_from_template(template, **kwargs):
        stock_holder = StockHolder.clone(template)
        if 'event_id' in kwargs:
            stock_holder.event_id = kwargs['event_id']
        stock_holder.save()
        return {template.id:stock_holder.id}

# stock based on quantity
class Stock(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Stock"
    id = Column(Identifier, primary_key=True)
    quantity = Column(Integer)
    performance_id = Column(Identifier, ForeignKey('Performance.id'), nullable=False)
    stock_holder_id = Column(Identifier, ForeignKey('StockHolder.id'), nullable=True)
    stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=True)
    locked_at = Column(DateTime, nullable=True, default=None)

    stock_status = relationship("StockStatus", uselist=False, backref='stock')

    def count_vacant_quantity(self):
        if self.stock_type and self.stock_type.quantity_only:
            from altair.app.ticketing.cart.models import CartedProduct, CartedProductItem
            # 販売済みの座席数
            reserved_quantity = Stock.filter(Stock.id==self.id).join(Stock.product_items)\
                .join(ProductItem.ordered_product_items)\
                .join(OrderedProductItem.ordered_product)\
                .join(OrderedProduct.order)\
                .filter(Order.canceled_at==None)\
                .with_entities(func.sum(OrderedProductItem.quantity)).scalar() or 0
            # Cartで確保されている座席数
            reserved_quantity += Stock.filter(Stock.id==self.id).join(Stock.product_items)\
                .join(ProductItem.carted_product_items)\
                .join(CartedProductItem.carted_product)\
                .filter(CartedProduct.finished_at==None)\
                .with_entities(func.sum(CartedProductItem.quantity)).scalar() or 0
            vacant_quantity = self.quantity - reserved_quantity
        else:
            vacant_quantity = Seat.filter(Seat.stock_id==self.id)\
                .join(SeatStatus)\
                .filter(SeatStatus.status.in_([SeatStatusEnum.Vacant.v])).count()
        return vacant_quantity

    def save(self):
        case_add = False if hasattr(self, 'id') and self.id else True
        super(Stock, self).save()

        if case_add:
            # 登録時にStockStatusを作成
            stock_status = StockStatus(stock_id=self.id, quantity=self.quantity)
        else:
            # 更新時はquantityを更新、販売済み座席数を引く
            stock_status = StockStatus.filter_by(stock_id=self.id).with_lockmode('update').first()
            stock_status.quantity = self.count_vacant_quantity()
        stock_status.save()

    def delete(self, force=False):
        # 在庫が割り当てられている場合は削除できない
        if not force and (self.quantity > 0 or self.product_items):
            raise Exception(u'座席および席数の割当がある為、削除できません')

        # delete StockStatus
        self.stock_status.delete()

        super(Stock, self).delete()

    @staticmethod
    def get_default(performance_id):
        return Stock.filter_by(performance_id=performance_id).filter_by(stock_type_id=None).first()

    @staticmethod
    def create_default(event, performance_id=None, stock_type_id=None, stock_holder_id=None):
        '''
        初期状態のStockを生成する
          - デフォルト値となる"未選択"のStock
          - StockHolderのないStockType毎のStock
          - StockHolder × StockType分のStock
        既に該当のStockが存在する場合は、足りないStockのみ生成する
        '''
        performances = [Performance.get(performance_id)] if performance_id else event.performances
        stock_types = [StockType.get(stock_type_id)] if stock_type_id else event.stock_types
        stock_holders = [StockHolder.get(stock_holder_id)] if stock_holder_id else event.stock_holders

        # デフォルト値となる"未選択"のStockを生成
        for performance in performances:
            if not Stock.get_default(performance.id):
                stock = Stock(
                    performance_id=performance.id,
                    quantity=0
                )
                stock.save()

        created_stock_types = []
        for performance in performances:
            for stock_type in stock_types:
                # StockHolderのないStockType毎のStockを生成
                if not [stock for stock in performance.stocks if stock.stock_type_id == stock_type.id]:
                    stock = Stock(
                        performance_id=performance.id,
                        stock_type_id=stock_type.id,
                        stock_holder_id=None,
                        quantity=0
                    )
                    stock.save()

                # Performance × StockType × StockHolder分のStockを生成
                for stock_holder in stock_holders:
                    def stock_filter(stock):
                        return (stock.stock_type_id == stock_type.id and stock.stock_holder_id == stock_holder.id)
                    if not filter(stock_filter, performance.stocks):
                        stock = Stock(
                            performance_id=performance.id,
                            stock_type_id=stock_type.id,
                            stock_holder_id=stock_holder.id,
                            quantity=0
                        )
                        stock.save()
                        if stock_type.id not in created_stock_types:
                            created_stock_types.append(stock_type.id)

        ''' ProductItemの自動生成は行わない '''
        ## 生成したStockをProductに紐づけるProductItemを生成
        #for stock_type_id in created_stock_types:
        #    products = Product.filter(Product.seat_stock_type_id==stock_type_id).all()
        #    for product in products:
        #        ProductItem.create_default(product)

    @staticmethod
    def create_from_template(template, performance_id):
        stock = Stock.clone(template)
        stock.performance_id = performance_id
        stock.save()

        for template_product_item in template.product_items:
            ProductItem.create_from_template(template=template_product_item, stock_id=stock.id, performance_id=performance_id)

    @staticmethod
    def get_for_update(pid, stid):
        return Stock.filter(Stock.performance_id==pid, Stock.stock_type_id==stid, Stock.quantity>0).with_lockmode("update").first()

# stock based on quantity
class StockStatus(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockStatus"
    stock_id = Column(Identifier, ForeignKey('Stock.id'), primary_key=True)
    quantity = Column(Integer)

class TicketType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'TicketType'

    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(255), nullable=False)
    display_name = Column(Unicode(255), nullable=True)
    display_order = Column(Integer, nullable=False, default=1)
    public = Column(Boolean, nullable=False, default=True)
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    event_id = Column(Identifier, ForeignKey('Event.id'), nullable=False)
    stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=False)
    stock_holder_id = Column(Identifier, ForeignKey('StockHolder.id'), nullable=False)
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id'), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    deleted_at = Column(TIMESTAMP, nullable=True)

class Product(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Product'

    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    name = AnnotatedColumn(String(255), _a_label=_(u'商品名'))
    price = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'価格'))
    display_order = AnnotatedColumn(Integer, nullable=False, default=1, _a_label=_(u'表示順'))

    sales_segment_group_id = Column(Identifier, ForeignKey('SalesSegmentGroup.id'), nullable=True)
    sales_segment_group = relationship('SalesSegmentGroup', uselist=False, backref=backref('product', order_by='Product.display_order'))

    sales_segment_id = AnnotatedColumn(Identifier, ForeignKey('SalesSegment.id'), nullable=True, _a_label=_(u'販売区分'))
    sales_segment = relationship('SalesSegment', backref=backref('products', order_by='Product.display_order'))

    ticket_type_id = Column(Identifier, ForeignKey('TicketType.id'), nullable=True)

    seat_stock_type_id = AnnotatedColumn(Identifier, ForeignKey('StockType.id'), nullable=True, _a_label=_(u'席種'))
    seat_stock_type = relationship('StockType', uselist=False, backref=backref('product', order_by='Product.display_order'))

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref=backref('products', order_by='Product.display_order'))

    items = relationship('ProductItem', backref=backref('product', order_by='Product.display_order'))

    performances = association_proxy('items', 'performance')

    # 一般公開するか
    public = AnnotatedColumn(Boolean, nullable=False, default=True, _a_label=_(u'公開'))

    description = Column(Unicode(2000), nullable=True, default=None)

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref='products')

    stocks = association_proxy('items', 'stock')
    base_product_id = Column(Identifier, nullable=True)

    @staticmethod
    def find(performance_id=None, event_id=None, sales_segment_group_id=None, stock_id=None, include_deleted=False):
        query = DBSession.query(Product, include_deleted=include_deleted)
        if performance_id:
            query = query.join(Product.items).filter(ProductItem.performance_id==performance_id)
        if event_id:
            query = query.filter(Product.event_id==event_id)
        if sales_segment_group_id:
            query = query.filter(Product.sales_segment_group_id==sales_segment_id)
        if stock_id:
            if not performance_id:
                query = query.join(Product.items)
            query = query.filter(ProductItem.stock_id==stock_id)
        return query.all()

    @staticmethod
    def create_default(stock_type=None):
        '''
        StockType追加時に、座席(StockType.is_seatが真)のProductならデフォルトのProductを自動生成する
        '''
        if stock_type.is_seat:
            # Productを生成
            product = Product(
                name=stock_type.name,
                price=0,
                event_id=stock_type.event_id,
                seat_stock_type_id=stock_type.id
            )
            product.save()

    def add(self):
        super(Product, self).add()

        ''' ProductItemの自動生成は行わない '''
        ## Performance数分のProductItemを生成
        #ProductItem.create_default(product=self)

    def delete(self):
        # 既に抽選申込されている場合は削除できない
        if self.lot_entry_products:
            raise Exception(u'抽選申込がある為、削除できません')

        # delete ProductItem
        for product_item in self.items:
            product_item.delete()

        super(Product, self).delete()

    def get_quantity_power(self, stock_type, performance_id):
        """ 数量倍率 """
        perform_items = ProductItem.query.filter(ProductItem.product==self).filter(ProductItem.performance_id==performance_id).all()
        return sum([pi.quantity for pi in perform_items if pi.stock.stock_type == stock_type])


    @deprecation.deprecate(u"商品が公演づきになったので、このクエリは不要")
    def items_by_performance_id(self, id):
        return ProductItem.filter_by(performance_id=id)\
                          .filter_by(product_id=self.id).all()

    def get_for_update(self):
        for item in self.items:
            if item.get_for_update() == None:
                return False
        return True

    def get_out_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity += 1
            item.seatStatus.status = SeatStatusEnum.Vacant.v
        DBSession.flush()
        return True

    def put_in_cart(self):
        if self.get_for_update() == False:
            return False
        for item in self.items:
            item.stock.quantity -= 1
            item.seatStatus.status = SeatStatusEnum.InCart.v
        DBSession.flush()
        return True

    def get_cms_data(self):
        data = {
            'id':self.id,
            'name':self.name,
            'price':floor(self.price),
            'seat_type':self.seat_type(),
            'display_order':self.display_order,
        }
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    def seat_type(self):
        return self.seat_stock_type.name if self.seat_stock_type else ''

    @staticmethod
    def create_from_template(template, with_product_items=False, **kwargs):
        product = Product.clone(template)
        product.event_id = None
        product.base_product_id = None
        product.sales_segment_group_id = None
        if 'event_id' in kwargs:
            product.event_id = kwargs['event_id']
        if 'performance_id' in kwargs:
            product.performance_id = kwargs['performance_id']
        if 'stock_type' in kwargs:
            product.seat_stock_type_id = kwargs['stock_type'][template.seat_stock_type_id]
        if 'sales_segment' in kwargs:
            # 販売区分なしの場合の product もありえる
            product.sales_segment_id = template.sales_segment_id and kwargs['sales_segment'][template.sales_segment_id]
        product.save()

        if with_product_items:
            stock_holder_id = kwargs['stock_holder_id'] if 'stock_holder_id' in kwargs else None
            for template_product_item in template.items:
                ProductItem.create_from_template(template=template_product_item, product_id=product.id, stock_holder_id=stock_holder_id)

        return {template.id:product.id}

    def num_tickets(self, pdmp):
        '''この Product に関わるすべての Ticket の数'''
        return DBSession.query(func.sum(ProductItem.quantity)) \
            .filter(Ticket_TicketBundle.ticket_bundle_id == ProductItem.ticket_bundle_id) \
            .filter((Ticket.id == Ticket_TicketBundle.ticket_id) & (Ticket.deleted_at == None)) \
            .filter((ProductItem.product_id == self.id) & (ProductItem.deleted_at == None)) \
            .filter((Ticket.ticket_format_id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat_DeliveryMethod.deleted_at == None)) \
            .filter((TicketFormat.id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat.deleted_at == None)) \
            .filter(TicketFormat_DeliveryMethod.delivery_method_id == pdmp.delivery_method_id) \
            .scalar() or 0

    def num_priced_tickets(self, pdmp):
        '''この Product に関わるTicketのうち、発券手数料を取るもの (額面があるもの)'''
        return DBSession.query(func.sum(ProductItem.quantity)) \
            .filter(Ticket_TicketBundle.ticket_bundle_id == ProductItem.ticket_bundle_id) \
            .filter((Ticket.id == Ticket_TicketBundle.ticket_id) & (Ticket.deleted_at == None)) \
            .filter((ProductItem.product_id == self.id) & (ProductItem.deleted_at == None)) \
            .filter((Ticket.ticket_format_id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat_DeliveryMethod.deleted_at == None)) \
            .filter((TicketFormat.id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat.deleted_at == None)) \
            .filter(TicketFormat_DeliveryMethod.delivery_method_id == pdmp.delivery_method_id) \
            .filter(Ticket.priced == True) \
            .scalar() or 0

    def has_lot_entry_products(self):
        from altair.app.ticketing.lots.models import LotEntryProduct
        return bool(LotEntryProduct.query.filter(LotEntryProduct.product_id==self.id).count())


class SeatIndexType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__  = "SeatIndexType"
    id             = Column(Identifier, primary_key=True)
    venue_id       = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'))
    name           = Column(String(255), nullable=False)
    seat_indexes   = relationship('SeatIndex', backref='seat_index_type')

    @staticmethod
    def create_from_template(template, venue_id):
        seat_index_type = SeatIndexType.clone(template)
        seat_index_type.venue_id = venue_id
        seat_index_type.save()
        return {template.id:seat_index_type.id}

class SeatIndex(Base, BaseModel):
    __tablename__      = "SeatIndex"
    seat_index_type_id = Column(Identifier, ForeignKey('SeatIndexType.id', ondelete='CASCADE'), primary_key=True)
    seat_id            = Column(Identifier, ForeignKey('Seat.id', ondelete='CASCADE'), primary_key=True)
    index              = Column(Integer, nullable=False)
    seat               = relationship('Seat', backref='indexes')

class OrganizationTypeEnum(StandardEnum):
    Standard = 1

class Organization(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Organization"
    id = Column(Identifier, primary_key=True)
    name = AnnotatedColumn(String(255), _a_label=(u"名称"))
    code = Column(String(3))  # 2桁英字大文字のみ
    short_name = Column(String(32), nullable=False, index=True, doc=u"templateの出し分けなどに使う e.g. %(short_name)s/index.html")
    client_type = Column(Integer)
    contact_email = Column(String(255))
    prefecture = Column(String(64), nullable=False, default=u'')
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    status = Column(Integer)

    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship("User", uselist=False, backref=backref('organization', uselist=False))

    def get_setting(self, name):
        for setting in self.settings:
            if setting.name == name:
                return setting
        raise Exception, "organization; id={0} does'nt have {1} setting".format(self.id, name)

    @property
    def setting(self):
        return self.get_setting(u'default')

    @property
    def point_feature_enabled(self):
        return self.setting.point_type is not None

    def get_cms_data(self):
        return {"organization_id": self.id, "organization_source": "oauth"}
    

orders_seat_table = Table("orders_seat", Base.metadata,
    Column("seat_id", Identifier, ForeignKey("Seat.id")),
    Column("OrderedProductItem_id", Identifier, ForeignKey("OrderedProductItem.id")),
)

class ShippingAddressMixin(object):
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

class ShippingAddress(Base, BaseModel, WithTimestamp, LogicallyDeleted, ShippingAddressMixin):
    __tablename__ = 'ShippingAddress'
    __clone_excluded__ = ['user', 'cart', 'lot_entries']

    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref='shipping_addresses')
    email_1 = Column(Unicode(255))
    email_2 = Column(Unicode(255))
    nick_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    first_name_kana = Column(String(255))
    last_name_kana = Column(String(255))
    sex = Column(Integer)
    zip = Column(String(255))
    country = Column(String(255))
    prefecture = Column(String(255), nullable=False, default=u'')
    city = Column(String(255), nullable=False, default=u'')
    address_1 = Column(String(255), nullable=False, default=u'')
    address_2 = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))

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

class OrderCancelReasonEnum(StandardEnum):
    User = (1, u'お客様都合')
    Promoter = (2, u'主催者都合')
    CallOff = (3, u'中止')

class Order(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Order'
    __table_args__= (
        UniqueConstraint('order_no', 'branch_no', name="ix_Order_order_no_branch_no"),
        )
    __clone_excluded__ = ['cart', 'ordered_from', 'payment_delivery_pair', 'performance', 'user', '_attributes', 'refund', 'operator', 'lot_entries', 'lot_wishes', 'point_grant_history_entries', 'sales_segment']

    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User')
    shipping_address_id = Column(Identifier, ForeignKey("ShippingAddress.id"))
    shipping_address = relationship('ShippingAddress', backref='order')
    organization_id = Column(Identifier, ForeignKey("Organization.id"))
    ordered_from = relationship('Organization', backref='orders')
    operator_id = Column(Identifier, ForeignKey("Operator.id"))
    operator = relationship('Operator', uselist=False)
    channel = Column(Integer, nullable=True)

    items = relationship('OrderedProduct')
    total_amount = Column(Numeric(precision=16, scale=2), nullable=False)
    system_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    
    special_fee_name = Column(String(255), nullable=False, default="")
    special_fee = Column(Numeric(precision=16, scale=2), nullable=False, default=0)
    
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)

    multicheckout_approval_no = Column(Unicode(255), doc=u"マルチ決済受領番号")

    payment_delivery_method_pair_id = Column(Identifier, ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = relationship("PaymentDeliveryMethodPair", backref='orders')

    paid_at = Column(DateTime, nullable=True, default=None)
    delivered_at = Column(DateTime, nullable=True, default=None)
    canceled_at = Column(DateTime, nullable=True, default=None)
    refund_id = Column(Identifier, ForeignKey('Refund.id'))
    refunded_at = Column(DateTime, nullable=True, default=None)

    order_no = Column(String(255))
    branch_no = Column(Integer, nullable=False, default=1, server_default='1')
    note = Column(UnicodeText, nullable=True, default=None)

    issued = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=True, default=None, doc=u"印刷可能な情報伝達済み")
    printed_at = Column(DateTime, nullable=True, default=None, doc=u"実発券済み")

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref="orders")

    _attributes = relationship("OrderAttribute", backref='order', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderAttribute(name=k, value=v))

    card_brand = Column(Unicode(20))
    card_ahead_com_code = Column(Unicode(20), doc=u"仕向け先企業コード")
    card_ahead_com_name = Column(Unicode(20), doc=u"仕向け先企業名")

    fraud_suspect = Column(Boolean, nullable=True, default=None)
    browserid = Column(String(40))

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment', backref='orders')

    def is_canceled(self):
        return bool(self.canceled_at)

    def is_issued(self):
        """
        チケット券面が発行済みかどうかを返す。
        Order, OrderedProductItem, OrderedProductItemTokenという階層中にprinted_atが存在。
        """
        if self.issued_at:
            return True

        qs = OrderedProductItem.query.filter_by(deleted_at=None)\
            .filter(OrderedProduct.order_id==self.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProductItem.issued_at==None)
        return qs.first() is None

    def is_printed(self):
        """
        チケット券面が印刷済みかどうかを返す。(順序としてはissued -> printed)

        Order, OrderedProductItem, OrderedProductItemTokenという階層中にprinted_atが存在。
        各下位オブジェクトが全てprintedであれば、printed = True
        """
        if self.printed_at:
            return True

        qs = OrderedProductItem.query.filter_by(deleted_at=None)\
            .filter(OrderedProduct.order_id==self.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProductItem.printed_at==None)
        return qs.first() is None

    @classmethod
    def __declare_last__(cls):
        cls.queued = column_property(
                exists(select('*') \
                    .select_from(TicketPrintQueueEntry.__table__ \
                        .join(OrderedProductItem.__table__) \
                        .join(OrderedProduct.__table__)) \
                    .where(OrderedProduct.order_id==cls.id) \
                    .where(TicketPrintQueueEntry.processed_at==None)),
                deferred=True)

    @property
    def payment_plugin_id(self):
        return self.payment_delivery_pair.payment_method.payment_plugin_id

    @property
    def delivery_plugin_id(self):
        return self.payment_delivery_pair.delivery_method.delivery_plugin_id

    @property
    def sej_order(self):
        return get_sej_order(self.order_no)

    @property
    def status(self):
        if self.canceled_at:
            return 'canceled'
        elif self.delivered_at:
            return 'delivered'
        else:
            return 'ordered'

    @property
    def payment_status(self):
        if self.refund_id and not self.refunded_at:
            return 'refunding'
        elif self.refunded_at:
            return 'refunded'
        elif self.paid_at:
            return 'paid'
        else:
            return 'unpaid'

    @property
    def cancel_reason(self):
        return self.refund.cancel_reason if self.refund else None

    @property
    def prev(self):
        return DBSession.query(Order, include_deleted=True).filter_by(order_no=self.order_no).filter_by(branch_no=self.branch_no-1).one()

    @property
    def checkout(self):
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.checkout.models import Checkout
        return Cart.query.filter(Cart._order_no==self.order_no).join(Checkout).with_entities(Checkout).first()

    @property
    def is_inner_channel(self):
        return self.channel in [ChannelEnum.INNER.v, ChannelEnum.IMPORT.v]

    def can_change_status(self, status):
        # 決済ステータスはインナー予約のみ変更可能
        if status == 'paid':
            return (self.status == 'ordered' and self.payment_status == 'unpaid' and self.is_inner_channel)
        elif status == 'unpaid':
            return (self.status == 'ordered' and self.payment_status == 'paid' and self.is_inner_channel)
        else:
            return False

    def can_cancel(self):
        # 受付済のみキャンセル可能、払戻時はキャンセル不可
        if self.status == 'ordered' and self.payment_status in ('unpaid', 'paid'):
            # コンビニ決済は未入金のみキャンセル可能
            payment_plugin_id = self.payment_delivery_pair.payment_method.payment_plugin_id
            if payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID and self.payment_status != 'unpaid':
                return False
            # コンビニ引取は未発券のみキャンセル可能
            delivery_plugin_id = self.payment_delivery_pair.delivery_method.delivery_plugin_id
            if delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID and self.is_issued():
                return False
            return True
        return False

    def can_refund(self):
        # 入金済または払戻予約のみ払戻可能
        return (self.status == 'ordered' and self.payment_status in ['paid', 'refunding'])

    def can_deliver(self):
        # 受付済のみ配送済に変更可能
        # インナー予約は常に、それ以外は入金済のみ変更可能
        return self.status == 'ordered' and (self.is_inner_channel or self.payment_status == 'paid')

    def can_delete(self):
        # キャンセルのみ論理削除可能
        return self.status == 'canceled'

    def cancel(self, request, payment_method=None, now=None):
        now = now or datetime.now()
        if not self.can_refund() and not self.can_cancel():
            logger.info('order (%s) cannot cancel status (%s, %s)' % (self.id, self.status, self.payment_status))
            return False

        '''
        決済方法ごとに払戻処理
        '''
        if payment_method:
            ppid = payment_method.payment_plugin_id
        else:
            ppid = self.payment_delivery_pair.payment_method.payment_plugin_id
        if not ppid:
            return False

        # インナー予約の場合はAPI決済していないのでスキップ
        # ただしコンビニ決済はインナー予約でもAPIで通知しているので処理する
        if self.is_inner_channel and ppid != plugins.SEJ_PAYMENT_PLUGIN_ID:
            logger.info(u'インナー予約のキャンセルなので決済払戻処理をスキップ %s' % self.order_no)

        # クレジットカード決済
        elif ppid == plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID:
            # 入金済みなら決済をキャンセル
            if self.payment_status in ['paid', 'refunding']:
                # 売り上げキャンセル
                from altair.multicheckout import api as multicheckout_api

                order_no = self.order_no
                if request.registry.settings.get('multicheckout.testing', False):
                    order_no = self.order_no + "00"
                organization = Organization.get(self.organization_id)
                request.altair_checkout3d_override_shop_name = organization.setting.multicheckout_shop_name

                # キャンセルAPIでなく売上一部取消APIを使う
                # - 払戻期限を越えてもキャンセルできる為
                # - 売上一部取消で減額したあと、キャンセルAPIをつかうことはできない為
                # - ただし、売上一部取消APIを有効にする以前に予約があったものはキャンセルAPIをつかう
                if self.payment_status in ['refunding']:
                    logger.info(u'売上一部取消APIで払戻 %s' % self.order_no)
                    prev = self.prev
                    total_amount = prev.refund.item(prev) + prev.refund.fee(prev)
                    multi_checkout_result = multicheckout_api.checkout_sales_part_cancel(request, order_no, total_amount, 0)
                else:
                    sales_part_cancel_enabled_from = '2012-12-03 08:00'
                    if self.created_at < datetime.strptime(sales_part_cancel_enabled_from, "%Y-%m-%d %H:%M"):
                        logger.info(u'キャンセルAPIでキャンセル %s' % self.order_no)
                        multi_checkout_result = multicheckout_api.checkout_sales_cancel(request, order_no)
                    else:
                        logger.info(u'売上一部取消APIで全額取消 %s' % self.order_no)
                        multi_checkout_result = multicheckout_api.checkout_sales_part_cancel(request, order_no, self.total_amount, 0)

                error_code = ''
                if multi_checkout_result.CmnErrorCd and multi_checkout_result.CmnErrorCd != '000000':
                    error_code = multi_checkout_result.CmnErrorCd
                elif multi_checkout_result.CardErrorCd and multi_checkout_result.CardErrorCd != '000000':
                    error_code = multi_checkout_result.CardErrorCd

                if error_code:
                    logger.error(u'クレジットカード決済のキャンセルに失敗しました。 %s' % error_code)
                    return False

                self.multi_checkout_approval_no = multi_checkout_result.ApprovalNo

        # 楽天あんしん支払いサービス
        elif ppid == plugins.CHECKOUT_PAYMENT_PLUGIN_ID:
            # 入金済みなら決済をキャンセル
            if self.payment_status in ['paid', 'refunding']:
                from altair.app.ticketing.checkout import api as checkout_api
                from altair.app.ticketing.core import api as core_api
                service = checkout_api.get_checkout_service(request, self.ordered_from, core_api.get_channel(self.channel))
                checkout = self.checkout
                if self.payment_status == 'refunding':
                    # 払戻(合計100円以上なら注文金額変更API、0円なら注文キャンセルAPIを使う)
                    if self.total_amount >= 100:
                        result = service.request_change_order([checkout.orderControlId])
                        # オーソリ済みになるので売上バッチの処理対象になるようにsales_atをクリア
                        checkout.sales_at = None
                        checkout.save()
                    elif self.total_amount == 0:
                        result = service.request_cancel_order([checkout.orderControlId])
                    else:
                        logger.error(u'0円以上100円未満の注文は払戻できません (order_no=%s)' % self.order_no)
                        return False
                    if 'statusCode' in result and result['statusCode'] != '0':
                        logger.error(u'あんしん決済を払戻できませんでした %s' % result)
                        return False
                else:
                    # 売り上げキャンセル
                    logger.debug(u'売り上げキャンセル')
                    result = service.request_cancel_order([checkout.orderControlId])
                    if 'statusCode' in result and result['statusCode'] != '0':
                        logger.error(u'あんしん決済をキャンセルできませんでした %s' % result)
                        return False

        # コンビニ決済 (セブン-イレブン)
        elif ppid == plugins.SEJ_PAYMENT_PLUGIN_ID:
            sej_order = self.sej_order

            # 未入金ならコンビニ決済のキャンセル通知
            if self.payment_status == 'unpaid':
                result = sej_api.cancel_sej_order(sej_order, self.organization_id)
                if not result:
                    return False

            # 入金済み、払戻予約ならコンビニ決済の払戻通知
            elif self.payment_status in ['paid', 'refunding']:
                result = sej_api.refund_sej_order(sej_order, self.organization_id, self, now)
                if not result:
                    return False

        # 窓口支払
        elif ppid == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID:
            pass

        '''
        配送方法ごとに取消処理
        '''
        # コンビニ受取
        dpid = self.payment_delivery_pair.delivery_method.delivery_plugin_id
        if dpid == plugins.SEJ_DELIVERY_PLUGIN_ID and ppid != plugins.SEJ_PAYMENT_PLUGIN_ID:
            sej_order = self.sej_order
            # SejAPIでエラーのケースではSejOrderはつくられないのでスキップ
            if sej_order:
                result = sej_api.cancel_sej_order(sej_order, self.organization_id)
                if not result:
                    logger.info('SejOrder (order_no=%s) cancel error' % self.order_no)
                    return False
            else:
                logger.info('skip cancel delivery method. SejOrder not found (order_no=%s)' % self.order_no)

        # 在庫を戻す
        logger.info('try release stock (order_no=%s)' % self.order_no)
        self.release()
        if self.payment_status != 'refunding':
            self.mark_canceled()
        if self.payment_status in ['paid', 'refunding']:
            self.mark_refunded()

        self.save()
        logger.info('success order cancel (order_no=%s)' % self.order_no)

        return True

    def mark_canceled(self, now=None):
        self.canceled_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_refunded(self, now=None):
        self.refunded_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_delivered(self, now=None):
        self.delivered_at = now or datetime.now() # SAFE TO USE datetime.now() HERE

    def mark_paid(self, now=None):
        self.paid_at = now or datetime.now()

    def mark_issued_or_printed(self, issued=False, printed=False, now=None):
        if not issued and not printed:
            raise ValueError('either issued or printed must be True')

        if printed:
            if not (issued or self.issued):
                raise Exception('trying to mark an order as printed that has not been issued')

        now = now or datetime.now()
        delivery_plugin_id = self.payment_delivery_pair.delivery_method.delivery_plugin_id

        for ordered_product in self.items:
            for item in ordered_product.ordered_product_items:
                reissueable = item.product_item.ticket_bundle.reissueable(delivery_plugin_id)
                if issued:
                    if self.issued:
                        if not reissueable:
                            logger.warning("Trying to reissue a ticket for Order (id=%d) that contains OrderedProductItem (id=%d) associated with a ticket which is not marked reissueable" % (self.id, item.id))
                    item.issued = True
                    item.issued_at = now
                if printed:
                    item.printed_at = now
        if issued:
            self.issued = True
            self.issued_at = now
        if printed:
            self.printed_at = now

    @staticmethod
    def reserve_refund(kwargs):
        refund = Refund(**kwargs)
        refund.save()

    def call_refund(self, request):
        # 払戻対象の金額をクリア
        order = Order.clone(self, deep=True)
        if self.refund.include_system_fee:
            order.system_fee = 0
        if self.refund.include_special_fee:
            order.special_fee = 0
        if self.refund.include_transaction_fee:
            order.transaction_fee = 0
        if self.refund.include_delivery_fee:
            order.delivery_fee = 0
        if self.refund.include_item:
            for ordered_product in order.items:
                ordered_product.price = 0
                for ordered_product_item in ordered_product.ordered_product_items:
                    ordered_product_item.price = 0
        order.total_amount = sum(o.price * o.quantity for o in order.items) + order.system_fee + order.transaction_fee + order.delivery_fee

        try:
            return order.cancel(request, self.refund.payment_method)
        except Exception, e:
            logger.error(u'払戻処理でエラーが発生しました (%s)' % e.message)
        return False

    def release(self):
        # 在庫を解放する
        for product in self.ordered_products:
            product.release()

    def change_status(self, status):
        if self.can_change_status(status):
            if status == 'paid':
                self.mark_paid()
            if status == 'unpaid':
                self.paid_at = None
            self.save()
            return True
        return False

    def delivered(self):
        if self.can_deliver():
            self.mark_delivered()
            self.save()
            return True
        else:
            return False

    def undelivered(self):
        self.delivered_at = None
        self.save()
        return True

    def delete(self, force=False):
        if not self.can_delete() and not force:
            logger.info('order (%s) cannot delete status (%s)' % (self.id, self.status))
            raise Exception(u'キャンセル以外は非表示にできません')
            
        # delete OrderedProduct
        for ordered_product in self.items:
            ordered_product.delete()

        # delete ShippingAddress
        if self.shipping_address:
            self.shipping_address.delete()

        super(Order, self).delete()

    @classmethod
    def clone(cls, origin, **kwargs):
        new_order = super(Order, cls).clone(origin, **kwargs)
        new_order.branch_no = origin.branch_no + 1
        new_order.attributes = origin.attributes
        new_order.created_at = origin.created_at
        for op, nop in itertools.izip(origin.items, new_order.items):
            for opi, nopi in itertools.izip(op.ordered_product_items, nop.ordered_product_items):
                nopi.seats = opi.seats
                nopi.attributes = opi.attributes

        new_order.add()
        origin.delete(force=True)
        return Order.get(new_order.id, new_order.organization_id)

    @staticmethod
    def get(id, organization_id, include_deleted=False):
        query = DBSession.query(Order, include_deleted=include_deleted).filter_by(id=id, organization_id=organization_id)
        return query.first()

    @classmethod
    def create_from_cart(cls, cart):
        order = cls(
            order_no=cart.order_no,
            total_amount=cart.total_amount,
            shipping_address=cart.shipping_address,
            payment_delivery_pair=cart.payment_delivery_pair,
            system_fee=cart.system_fee,
            special_fee_name=cart.special_fee_name,
            special_fee=cart.special_fee,
            transaction_fee=cart.transaction_fee,
            delivery_fee=cart.delivery_fee,
            performance=cart.performance,
            sales_segment=cart.sales_segment,
            organization_id=cart.sales_segment.sales_segment_group.event.organization_id,
            channel=cart.channel,
            operator=cart.operator,
            user=cart.shipping_address and cart.shipping_address.user
            )

        for product in cart.products:
            # この ordered_product はコンストラクタに order を指定しているので
            # 勝手に order.ordered_products に追加されるから、append は不要
            ordered_product = OrderedProduct(
                order=order, product=product.product, price=product.product.price, quantity=product.quantity)
            for item in product.items:
                ordered_product_item = OrderedProductItem(
                    ordered_product=ordered_product,
                    product_item=item.product_item,
                    price=item.product_item.price,
                    quantity=item.product_item.quantity * product.quantity,
                    seats=item.seats
                    )
                for i, seat in ordered_product_item.iterate_serial_and_seat():
                    token = OrderedProductItemToken(
                        serial = i, 
                        seat = seat, 
                        valid=True #valid=Falseの時は何時だろう？
                        )
                    ordered_product_item.tokens.append(token)
        DBSession.flush() # これとっちゃだめ
        return order

    @staticmethod
    def filter_by_performance_id(id):
        performance = Performance.get(id)
        if not performance:
            return None

        return Order.filter_by(organization_id=performance.event.organization_id)\
            .join(Order.ordered_products)\
            .join(OrderedProduct.ordered_product_items)\
            .join(OrderedProductItem.product_item)\
            .filter(ProductItem.performance_id==id)\
            .distinct()

def no_filter(value):
    return value

class OrderAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderAttribute"
    order_id  = Column(Identifier, ForeignKey('Order.id'), primary_key=True, nullable=False)
    name = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(1023))

class OrderedProductAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "OrderedProductAttribute"
    ordered_product_item_id  = Column(Identifier, ForeignKey('OrderedProductItem.id'), primary_key=True, nullable=False)
    name = Column(String(255), primary_key=True, nullable=False)
    value = Column(String(1023))

class OrderedProduct(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProduct'
    __clone_excluded__ = ['order_id', 'product']

    id = Column(Identifier, primary_key=True)
    order_id = Column(Identifier, ForeignKey("Order.id"))
    order = relationship('Order', backref='ordered_products')
    product_id = Column(Identifier, ForeignKey("Product.id"))
    product = relationship('Product', backref='ordered_products')
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    quantity = Column(Integer)

    @property
    def seats(self):
        return sorted(itertools.chain.from_iterable(i.seatdicts for i in self.ordered_product_items),
            key=operator.itemgetter('l0_id'))

    @property
    def seat_quantity(self):
        quantity = 0
        for item in self.ordered_product_items:
            if item.product_item.stock_type.is_seat:
                quantity += item.quantity
        return quantity

    def release(self):
        # 在庫を解放する
        for item in self.ordered_product_items:
            item.release()

    def delete(self):
        # delete OrderedProductItem
        for ordered_product_item in self.ordered_product_items:
            ordered_product_item.delete()

        super(OrderedProduct, self).delete()

class OrderedProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProductItem'
    __clone_excluded__ = ['ordered_product_id', 'product_item', 'seats', '_attributes']

    id = Column(Identifier, primary_key=True)
    ordered_product_id = Column(Identifier, ForeignKey("OrderedProduct.id"))
    ordered_product = relationship('OrderedProduct', backref='ordered_product_items')
    product_item_id = Column(Identifier, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem', backref='ordered_product_items')
    issued_at = Column(DateTime, nullable=True, default=None)
    printed_at = Column(DateTime, nullable=True, default=None)
    seats = relationship("Seat", secondary=orders_seat_table, backref='ordered_product_items')
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    _attributes = relationship("OrderedProductAttribute", backref='ordered_product_item', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderedProductAttribute(name=k, value=v))

    # 実際の購入数
    quantity = Column(Integer, nullable=False, default=1, server_default='1')

    @property
    def seat_statuses_for_update(self):
        if len(self.seats) > 0:
            return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).with_lockmode('update').all()
        return []

    @property
    def name(self):
        if not self.seats:
            return u""
        return u', '.join([(seat.name) for seat in self.seats if seat.name])

    @property
    def seat_statuses(self):
        """ 確保済の座席ステータス
        """
        return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).all()

    def release(self):
        # 座席開放
        cancellable_status = [
            int(SeatStatusEnum.Ordered),
            int(SeatStatusEnum.Reserved),
        ]
        for seat_status in self.seat_statuses_for_update:
            logger.info('trying to release seat (id=%d)' % seat_status.seat_id)
            if seat_status.status not in cancellable_status:
                logger.info('not releasing OrderedProductItem (id=%d, seat_id=%d, status=%d) for safety' % (self.id, seat_status.seat_id, seat_status.status))
                raise InvalidStockStateError("This order is associated with a seat (id=%d, status=%d) that is not marked ordered" % (seat_status.seat_id, seat_status.status))
            else:
                logger.info('setting status of seat (id=%d, status=%d) to Vacant (%d)' % (seat_status.seat_id, seat_status.status, int(SeatStatusEnum.Vacant)))
                seat_status.status = int(SeatStatusEnum.Vacant)

        # 在庫数を戻す
        if self.product_item.stock.stock_type.quantity_only:
            release_quantity = self.quantity
        else:
            release_quantity = len(self.seats)
        stock_status = StockStatus.filter_by(stock_id=self.product_item.stock_id).with_lockmode('update').one()
        logger.info('restoring the quantity of stock (id=%s, quantity=%d) by +%d' % (stock_status.stock_id, stock_status.quantity, release_quantity))
        stock_status.quantity += release_quantity
        stock_status.save()
        logger.info('done for OrderedProductItem (id=%d)' % self.id)

    @property
    def seatdicts(self):
        return ({'name': s.name, 'l0_id': s.l0_id}
                for s in self.seats)

    def is_issued(self):
        return self.issued_at or self.tokens == [] or all(token.issued_at for token in self.tokens)

    def is_printed(self):
        return self.printed_at or self.tokens == [] or all(token.printed_at for token in self.tokens)

    @property
    def issued_at_status(self):
        total = len(self.tokens)
        issued_count = len([i for i in self.tokens if i.issued_at])
        return dict(issued=issued_count, total=total)

    def iterate_serial_and_seat(self):
        if self.seats:
            for i, s in enumerate(self.seats):
                yield i, s
        else:
            for i in xrange(self.quantity):
                yield i, None

class OrderedProductItemToken(Base,BaseModel, LogicallyDeleted):
    __tablename__ = "OrderedProductItemToken"
    __clone_excluded__ = ['seat']

    id = Column(Identifier, primary_key=True)
    ordered_product_item_id = Column(Identifier, ForeignKey("OrderedProductItem.id", ondelete="CASCADE"), nullable=False)
    item = relationship("OrderedProductItem", backref="tokens")
    seat_id = Column(Identifier, ForeignKey("Seat.id", ondelete='CASCADE'), nullable=True)
    seat = relationship("Seat", backref="tokens")
    serial = Column(Integer, nullable=False)
    key = Column(Unicode(255), nullable=True)    #今は使っていない。https://dev.ticketstar.jp/redmine/altair/issues/499#note-15
    valid = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=True, default=None)
    printed_at = Column(DateTime, nullable=True, default=None)
    refreshed_at = Column(DateTime, nullable=True, default=None)

    def is_printed(self):
        return self.printed_at and (self.refreshed_at is None or self.printed_at > self.refreshed_at)

class Ticket_TicketBundle(Base, BaseModel, LogicallyDeleted):
    __tablename__ = 'Ticket_TicketBundle'
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id', ondelete='CASCADE'), primary_key=True)
    ticket_id = Column(Identifier, ForeignKey('Ticket.id', ondelete='CASCADE'), primary_key=True)

class TicketFormat_DeliveryMethod(Base, BaseModel, LogicallyDeleted):
    __tablename__ = 'TicketFormat_DeliveryMethod'
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id', ondelete='CASCADE'), primary_key=True)
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id', ondelete='CASCADE'), primary_key=True)

class TicketFormat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketFormat"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=True)
    organization = relationship('Organization', uselist=False, backref='ticket_formats')
    delivery_methods = relationship('DeliveryMethod', secondary=TicketFormat_DeliveryMethod.__table__, backref='ticket_formats')
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

class Ticket(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Ticket.event_idがNULLのものはマスターデータ。これを雛形として実際にeventとひもづけるTicketオブジェクトを作成する。
    """
    __tablename__ = "Ticket"

    FLAG_ALWAYS_REISSUEABLE = 1
    FLAG_PRICED = 2

    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=True)
    organization = relationship('Organization', uselist=False, backref=backref('ticket_templates'))
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='tickets')
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id', ondelete='CASCADE'), nullable=False)
    ticket_format = relationship('TicketFormat', uselist=False, backref='tickets')
    name = Column(Unicode(255), nullable=False, default=u'')
    flags = Column(Integer, nullable=False, default=FLAG_PRICED)
    original_ticket_id = Column(Identifier, ForeignKey('Ticket.id', ondelete='SET NULL'), nullable=True)
    derived_tickets = relationship('Ticket', backref=backref('original_ticket', remote_side=[id]))
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

    def before_insert_or_update(self):
        if self.original_ticket and self.data != self.original_ticket.data:
            self.original_ticket_id = None

    @classmethod
    def templates_query(cls):
        return cls.filter_by(event_id=None)

    @property
    def drawing(self):
        return self.data["drawing"]

    @property
    def vars_defaults(self):
        return self.data.get("vars_defaults", {})

    def create_event_bound(self, event):
        new_object = self.__class__.clone(self)
        new_object.event_id = event.id
        new_object.original_ticket = self
        return new_object

    @staticmethod
    def create_from_template(template, **kwargs):
        ticket = Ticket.clone(template)
        if 'event_id' in kwargs:
            ticket.event_id = kwargs['event_id']
        ticket.original_ticket_id = template.id
        ticket.save()
        return {template.id:ticket.id}

    @hybrid_property
    def always_reissueable(self):
        return (self.flags & self.FLAG_ALWAYS_REISSUEABLE) != 0

    @always_reissueable.expression
    def priced(self):
        return self.flags.op('&')(self.FLAG_ALWAYS_REISSUEABLE) != 0

    @always_reissueable.setter
    def set_reissueable(self, value):
        if value:
            self.flags |= self.FLAG_ALWAYS_REISSUEABLE
        else:
            self.flags &= ~self.FLAG_ALWAYS_REISSUEABLE

    @hybrid_property
    def priced(self):
        return (self.flags & self.FLAG_PRICED) != 0

    @priced.expression
    def priced(self):
        return self.flags.op('&')(self.FLAG_PRICED) != 0

    @priced.setter
    def set_priced(self, value):
        if value:
            self.flags |= self.FLAG_PRICED
        else:
            self.flags &= ~self.FLAG_PRICED

for event_kind in ['before_insert', 'before_update']:
    event.listen(Ticket, event_kind, lambda mapper, conn, target: target.before_insert_or_update())

class TicketBundleAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketBundleAttribute" 
    id = Column(Identifier, primary_key=True)
    ticket_bundle_id = Column(Identifier, ForeignKey('TicketBundle.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(1023))

    __table_args__= (
        UniqueConstraint("ticket_bundle_id", "name", "deleted_at", name="ib_unique_1"), 
        )

class TicketPrintQueueEntry(Base, BaseModel):
    __tablename__ = "TicketPrintQueueEntry"
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'), nullable=True)
    operator = relationship('Operator', uselist=False)
    ordered_product_item_id = Column(Identifier, ForeignKey('OrderedProductItem.id'), nullable=True)
    ordered_product_item = relationship('OrderedProductItem')
    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=True)
    seat = relationship('Seat')
    ticket_id = Column(Identifier, ForeignKey('Ticket.id'), nullable=False)
    ticket = relationship('Ticket')
    summary = Column(Unicode(255), nullable=False, default=u'')
    data = deferred(Column(MutationDict.as_mutable(JSONEncodedDict(65536))))
    created_at = Column(TIMESTAMP, nullable=False,
                        default=datetime.now,
                        server_default=sqlf.current_timestamp())
    processed_at = Column(TIMESTAMP, nullable=True, default=None)
    masked_at = Column(TIMESTAMP, nullable=True, default=None)

    @property
    def drawing(self):
        return self.data["drawing"]

    @classmethod
    def enqueue(self, operator, ticket, data, summary, ordered_product_item=None, seat=None):
        entry = TicketPrintQueueEntry(operator=operator, 
                                      ticket=ticket, 
                                      data=data, 
                                      summary=summary, 
                                      ordered_product_item=ordered_product_item, 
                                      seat=seat)
        DBSession.add(entry)
        DBSession.flush()

    @classmethod
    def peek(self, operator, ticket_format_id, order_id=None):
        q = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(processed_at=None, operator=operator, masked_at=None) \
            .filter(Ticket.ticket_format_id==ticket_format_id) \
            .options(joinedload(TicketPrintQueueEntry.seat))
        if order_id is not None:
            q = q.join(OrderedProductItem) \
                .join(OrderedProduct) \
                .filter(OrderedProduct.order_id==order_id)
        q = q.order_by(*self.printing_order_condition())
        return q.all()

    @classmethod
    def printing_order_condition(cls):
        return (TicketPrintQueueEntry.created_at, TicketPrintQueueEntry.id)


    @classmethod
    def dequeue(self, ids, now=None):
        logger.info("TicketPrintQueueEntry dequeue ids: {0}".format(ids))
        now = now or datetime.now() # SAFE TO USE datetime.now() HERE
        entries = DBSession.query(TicketPrintQueueEntry) \
            .with_lockmode("update") \
            .outerjoin(TicketPrintQueueEntry.ordered_product_item) \
            .outerjoin(OrderedProductItem.ordered_product) \
            .outerjoin(OrderedProduct.order) \
            .filter(TicketPrintQueueEntry.id.in_(ids)) \
            .filter(TicketPrintQueueEntry.masked_at == None) \
            .filter(TicketPrintQueueEntry.processed_at == None) \
            .options(joinedload(TicketPrintQueueEntry.seat)) \
            .order_by(desc(TicketPrintQueueEntry.created_at)) \
            .all()
        if len(entries) == 0:
            return []
        relevant_orders = {}
        for entry in entries:
            entry.processed_at = now
            if entry.ordered_product_item is not None and entry.ordered_product_item.ordered_product is not None:
                order = entry.ordered_product_item.ordered_product.order
                entries = relevant_orders.get(order)
                if entries is None:
                    entries = relevant_orders[order] = []
                else:
                    if len(entries) > 1:
                        logger.info("More than one entry exist for the same order (%d)" % order.id)
                entries.append(entry)
            else:
                logger.info("TicketPrintQueueEntry #%d is not associated with the order" % entry.id)

        for order, entries in relevant_orders.items():
            for entry in entries:
                # XXX: this won't work right if multiple entries exist for the
                # same order.
                order.mark_issued_or_printed(issued=True, printed=True, now=now)
        return entries


    
from ..operators.models import Operator

class TicketCover(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    表紙。注文情報などが記載されている
    """
    __tablename__ = "TicketCover"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), default=u"", nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False, backref='ticket_covers')
    ticket_id = Column(Identifier, ForeignKey('Ticket.id'), nullable=False)
    ticket = relationship('Ticket',  backref=backref('cover'))
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id'))

    ## あとで伝搬サポートした時に移動
    @classmethod
    def get_from_order(cls, order):
        return TicketCover.query.filter_by(organization_id=order.organization_id).first() #todo: DeliveryMethod?

class TicketBundle(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketBundle"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), default=u"", nullable=False)
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='ticket_bundles')
    operator_id = Column(Identifier, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)
    attributes_ = relationship("TicketBundleAttribute", backref='ticket_bundle', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('attributes_', 'value', creator=lambda k, v: TicketBundleAttribute(name=k, value=v))
    tickets = relationship('Ticket', secondary=Ticket_TicketBundle.__table__, backref='bundles')
    product_items = relationship('ProductItem', backref='ticket_bundle')

    def replace_tickets(self, news):
        for ticket in self.tickets:
            self.tickets.remove(ticket)
        for ticket in news:
            self.tickets.append(ticket)

    def replace_product_items(self, news):
        for product_item in self.product_items:
            self.product_items.remove(product_item)
        for product_item in news:
            self.product_items.append(product_item)

    @staticmethod
    def create_from_template(template, **kwargs):
        ticket_bundle = TicketBundle.clone(template)
        if 'event_id' in kwargs:
            ticket_bundle.event_id = kwargs['event_id']

        for template_ticket in template.tickets:
            ticket = Ticket.get(kwargs['ticket'][template_ticket.id])
            ticket_bundle.tickets.append(ticket)

        ticket_bundle.attributes = template.attributes
        ticket_bundle.save()
        return {template.id:ticket_bundle.id}

    def reissueable(self, delivery_plugin_id):
        # XXX: このロジックははっきり言ってよろしくないので再実装する
        # (TicketBundleにフラグを持たせるべきか?)
        relevant_tickets = ApplicableTicketsProducer(self).include_delivery_id_ticket_iter(delivery_plugin_id)
        reissueable = False
        for ticket in relevant_tickets:
            if reissueable:
                if not ticket.always_reissueable:
                    logger.warning("TicketBundle (id=%d) contains tickets whose reissueable flag are inconsistent" % self.id)
            else:
                reissueable = ticket.always_reissueable
        return reissueable

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.product_items:
            raise Exception(u'関連づけされた商品がある為、削除できません')
        super(type(self), self).delete()

class TicketPrintHistory(Base, BaseModel, WithTimestamp):
    __tablename__ = "TicketPrintHistory"
    __clone_excluded__ = ['operator', 'seat', 'ticket']

    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'), nullable=True)
    operator = relationship('Operator', uselist=False)
    ordered_product_item_id = Column(Identifier, ForeignKey('OrderedProductItem.id'), nullable=True)
    ordered_product_item = relationship('OrderedProductItem', backref='print_histories')
    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=True)
    seat = relationship('Seat', backref='print_histories')
    item_token_id = Column(Identifier, ForeignKey('OrderedProductItemToken.id'), nullable=True)
    item_token = relationship('OrderedProductItemToken')
    order_id = Column(Identifier, ForeignKey('Order.id'), nullable=True)
    order = relationship('Order')
    ticket_id = Column(Identifier, ForeignKey('Ticket.id'), nullable=True)
    ticket = relationship('Ticket')

class PageFormat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "PageFormat"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    printer_name = Column(Unicode(255), nullable=False)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False, backref='page_formats')
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

    @property
    def drawing(self):
        return self.data["drawing"]

    @classmethod
    def enqueue(self, operator, data):
        '''
        '''
        DBSession.add(TicketPrintQueueEntry(data = data, operator = operator))

    @classmethod
    def dequeue_all(self, operator):
        '''
        '''
        return TicketPrintQueueEntry.filter_by(deleted_at = None, operator = operator).order_by('created_at desc').all()

class ExtraMailInfo(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "ExtraMailInfo"
    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id'), nullable=True)
    organization = relationship('Organization', uselist=False, backref=backref('extra_mailinfo', uselist=False))
    event_id = Column(Identifier, ForeignKey('Event.id'), nullable=True)
    event = relationship('Event', uselist=False, backref=backref('extra_mailinfo', uselist=False))
    performance_id = Column(Identifier, ForeignKey('Performance.id'), nullable=True)
    performance = relationship('Performance', uselist=False, backref=backref('extra_mailinfo', uselist=False))
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

    def is_valid(self):
        try:
            json.dumps(self.data, ensure_ascii=False)
            return True
        except Exception, e:
            self._errors = e
            return False

class MailTypeEnum(StandardEnum):
    PurchaseCompleteMail = 1
    PurchaseCancelMail = 2
    LotsAcceptedMail = 11
    LotsElectedMail = 12
    LotsRejectedMail = 13

MailTypeLabels = (u"購入完了メール", u"購入キャンセルメール", u"抽選申し込み完了メール", u"抽選当選通知メール", u"抽選落選通知メール")
assert(len(list(MailTypeEnum)) == len(MailTypeLabels))
MailTypeChoices = [(str(e) , label) for e, label in zip([enum.v for enum in sorted(iter(MailTypeEnum), key=lambda e: e.v)], MailTypeLabels)]
MailTypeEnum.dict = dict(MailTypeChoices)
MailTypeEnum.as_string = classmethod(lambda cls, e: cls.dict.get(str(e), ""))

class Host(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Host'
    __table_args__ = (
        UniqueConstraint('host_name', 'path'),
        )
    query = DBSession.query_property()

    id = Column(Identifier, primary_key=True)
    host_name = Column(Unicode(255))
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref="hosts")
    base_url = Column(Unicode(255))
    mobile_base_url = Column(Unicode(255))
    path = Column(Unicode(255))

    def __repr__(self):
        return u"{0.host_name} {0.path}".format(self).encode('utf-8')

class OrderNoSequence(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderNoSequence'
    id = Column(Identifier, primary_key=True)

    @classmethod
    def get_next_value(cls, name):
        seq = cls()
        DBSession.add(seq)
        DBSession.flush()
        return seq.id

class Mailer(object):
    def __init__(self, settings):
        self.settings = settings

    def create_message(self,
                       sender=None,
                       recipient=None,
                       subject=None,
                       body=None,
                       html=None,
                       encoding=None):

        encoding = self.settings['mail.message.encoding']
        if html:
            mime_type = 'html' 
            mime_text = html
        else:
            mime_type = 'plain'
            mime_text = body

        msg = MIMEText(mime_text.encode(encoding, 'ignore'), mime_type, encoding)
        msg['Subject'] = Header(subject, encoding)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate()
        self.message = msg

    def send(self, from_addr, to_addr):
        smtp = smtplib.SMTP(self.settings['mail.host'], self.settings['mail.port'])
        smtp.sendmail(from_addr, to_addr, self.message.as_string())
        smtp.close()

class ChannelEnum(StandardEnum):
    PC = 1
    Mobile = 2
    INNER = 3
    IMPORT = 4

class Refund(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Refund'

    id = Column(Identifier, primary_key=True)
    payment_method_id = Column(Identifier, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')
    include_system_fee = Column(Boolean, nullable=False, default=False)
    include_special_fee = Column(Boolean, nullable=False, default=False)
    include_transaction_fee = Column(Boolean, nullable=False, default=False)
    include_delivery_fee = Column(Boolean, nullable=False, default=False)
    include_item = Column(Boolean, nullable=False, default=False)
    cancel_reason = Column(String(255), nullable=True, default=None)
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    orders = relationship('Order', backref=backref('refund', uselist=False))

    def fee(self, order):
        total_fee = 0
        if self.include_system_fee:
            total_fee += order.system_fee
        if self.include_special_fee:
            total_fee += order.special_fee
        if self.include_transaction_fee:
            total_fee += order.transaction_fee
        if self.include_delivery_fee:
            total_fee += order.delivery_fee
        return total_fee

    def item(self, order):
        return sum(o.price * o.quantity for o in order.items) if self.include_item else 0


class SalesSegment(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'SalesSegment'
    query = DBSession.query_property()
    id = Column(Identifier, primary_key=True)
    start_at = AnnotatedColumn(DateTime, _a_label=_(u'販売開始'))
    end_at = AnnotatedColumn(DateTime, _a_label=_(u'販売終了'))
    upper_limit = AnnotatedColumn(Integer, _a_label=_(u'購入上限枚数'))
    order_limit = AnnotatedColumn(Integer, default=0,
                                  _a_label=_(u'購入回数制限'))

    seat_choice = AnnotatedColumn(Boolean, nullable=True, default=None,
                                  _a_label=_(u'座席選択可'))
    public = AnnotatedColumn(Boolean, default=True,
                                  _a_label=_(u'一般公開'))
    reporting = AnnotatedColumn(Boolean, nullable=False, default=True, server_default='1',
                                _a_label=_(u'レポート対象'))
    performance_id = AnnotatedColumn(Identifier, ForeignKey('Performance.id'),
                                _a_label=_(u'パフォーマンス'))
    performance = relationship("Performance", backref="sales_segments")
    sales_segment_group_id = AnnotatedColumn(Identifier, ForeignKey("SalesSegmentGroup.id"),
                                             _a_label=_(u'販売区分グループ'))
    sales_segment_group = relationship("SalesSegmentGroup", backref="sales_segments")
    margin_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0',
                                   _a_label=_(u'販売手数料率'))
    refund_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0',
                          _a_label=_(u'払戻手数料率'))
    printing_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0',
                          _a_label=_(u'印刷代金(円/枚)'))
    registration_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0',
                                       _a_label=_(u'登録手数料(円/公演)'))
    account_id = AnnotatedColumn(Identifier, ForeignKey('Account.id'),
                                 _a_label=_(u'配券元'))
    account = relationship('Account', backref='sales_segments')

    seat_stock_types = association_proxy('products', 'seat_stock_type')
    stocks = association_proxy_many('products', 'stock')
    payment_delivery_method_pairs = relationship("PaymentDeliveryMethodPair",
        secondary="SalesSegment_PaymentDeliveryMethodPair",
        backref="sales_segments",
        order_by="PaymentDeliveryMethodPair.id",
        cascade="all",
        collection_class=list)
    auth3d_notice = Column(UnicodeText)

    event_id = AnnotatedColumn(Identifier, ForeignKey("Event.id"),
                               _a_label=_(u'イベント'))
    event = relationship("Event", backref="sales_segments")
    organization_id = Column(Identifier, ForeignKey("Organization.id"))
    organization = relationship("Organization", backref="sales_segments")

    use_default_seat_choice = Column(Boolean)
    use_default_public = Column(Boolean)
    use_default_reporting = Column(Boolean)
    use_default_payment_delivery_method_pairs = Column(Boolean)
    use_default_start_at = Column(Boolean)
    use_default_end_at = Column(Boolean)
    use_default_upper_limit = Column(Boolean)
    use_default_order_limit = Column(Boolean)
    use_default_account_id = Column(Boolean)
    use_default_margin_ratio = Column(Boolean)
    use_default_refund_ratio = Column(Boolean)
    use_default_printing_fee = Column(Boolean)
    use_default_registration_fee = Column(Boolean)
    use_default_auth3d_notice = Column(Boolean)

    def has_stock_type(self, stock_type):
        return stock_type in self.seat_stock_types

    def has_stock(self, stock):
        return stock in self.stocks

    def available_payment_delivery_method_pairs(self, now):
        return [pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.is_available_for(self, now)]


    def query_orders_by_user(self, user):
        """ 該当ユーザーがこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.cart.models import Cart
        return DBSession.query(Order).filter(
            Order.user_id==user.id
        ).filter(
            Cart.order_id==Order.id
        ).filter(
            Cart.sales_segment_id==self.id
        )


    def query_orders_by_mailaddress(self, mailaddress):
        """ 該当メールアドレスによるこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.cart.models import Cart
        return DBSession.query(Order).filter(
            Order.shipping_address_id==ShippingAddress.id
        ).filter(
            or_(ShippingAddress.email_1 == mailaddress,
                ShippingAddress.email_2 == mailaddress)
        ).filter(
            Cart.order_id==Order.id
        ).filter(
            Cart.sales_segment_id==self.id
        )


    @hybrid_property
    def name(self):
        return self.sales_segment_group.name

    @hybrid_property
    def kind(self):
        return self.sales_segment_group.kind

    @hybrid_property
    def order(self):
        for i, k in enumerate(SalesSegmentKindEnum.order.v):
            if k == self.kind:
                return i
        return -1

    @hybrid_method
    def in_term(self, dt):
        return (self.start_at <= dt) and ((self.end_at is None) or (dt <= self.end_at))

    @in_term.expression
    def in_term_expr(self, dt):
        return (self.start_at <= dt) & ((None == self.end_at) | (dt <= self.end_at))


    @property
    def stocks(self):
        """ この販売区分で販売可能な在庫 
        商品 -> 商品アイテム -> 在庫
        """
        return Stock.query.filter(
                Stock.id==ProductItem.stock_id
            ).filter(
                ProductItem.product_id==Product.id
            ).filter(
                Product.sales_segment_id==self.id
            ).distinct(Stock.id)

    @staticmethod
    def set_search_condition(query, form):
        """TODO: query を構築するクラスを別に作る等したい"""
        if form.sort.data:
            direction = form.direction.data or 'desc'
            # XXX: injection safe?
            query = query.order_by(SalesSegment.__tablename__ + '.' + form.sort.data + ' ' + direction)

        condition = form.performance_id.data
        if condition:
            query = query.filter(SalesSegment.performance_id==condition)
        condition = form.public.data
        if condition:
            query = query.filter(SalesSegment.public==True)

        return query

    @property
    def kind_label(self):
        enum = getattr(SalesSegmentKindEnum, self.kind, None)
        if enum is None:
            return u"<不明>"
        else:
            return enum.v
        
    def get_cms_data(self):
        products = DBSession.query(Product, include_deleted=True).filter_by(sales_segment_id=self.id).all()
        data = {
            "id": self.id, 
            "kind_name": self.kind, 
            "kind_label": self.kind_label,
            "publicp": self.public,
            "group_publicp": self.sales_segment_group.public,
            "name": self.name,
            "start_on" : isodate.datetime_isoformat(self.start_at) if self.start_at else '', 
            "end_on" : isodate.datetime_isoformat(self.end_at) if self.end_at else '', 
            'group_id':self.sales_segment_group_id,
            'tickets':[p.get_cms_data() for p in products],
            'seat_choice':'true' if self.seat_choice else 'false',
            }
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    @staticmethod
    def create_from_template(template, **kwargs):
        sales_segment = SalesSegment.clone(template)
        if 'performance_id' in kwargs:
            sales_segment.performance_id = kwargs['performance_id']
        if 'sales_segment_group_id' in kwargs:
            sales_segment.sales_segment_group_id = kwargs['sales_segment_group_id']
            new_pdmps = []
            for org_pdmp in template.payment_delivery_method_pairs:
                new_pdmp = PaymentDeliveryMethodPair.query.filter(and_(
                    PaymentDeliveryMethodPair.sales_segment_group_id==sales_segment.sales_segment_group_id,
                    PaymentDeliveryMethodPair.payment_method_id==org_pdmp.payment_method_id,
                    PaymentDeliveryMethodPair.delivery_method_id==org_pdmp.delivery_method_id
                )).first()
                if new_pdmp:
                    new_pdmps.append(new_pdmp)
            sales_segment.payment_delivery_method_pairs = list()
            for new_pdmp in new_pdmps:
                sales_segment.payment_delivery_method_pairs.append(new_pdmp)
        else:
            sales_segment.payment_delivery_method_pairs = template.payment_delivery_method_pairs
        sales_segment.save()
        return {template.id:sales_segment.id}

    def delete(self):
        # delete Product
        for product in self.products:
            product.delete()
        super(type(self), self).delete()

    def get_amount(self, pdmp, product_quantities):
        return pdmp.per_order_fee + self.get_products_amount(pdmp, product_quantities)

    def get_transaction_fee(self, pdmp, product_quantities):
        return pdmp.transaction_fee_per_order + sum([
            (pdmp.transaction_fee_per_product + \
             pdmp.transaction_fee_per_ticket * product.num_priced_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_delivery_fee(self, pdmp, product_quantities):
        return pdmp.delivery_fee_per_order + sum([
            (pdmp.delivery_fee_per_product + \
             pdmp.delivery_fee_per_ticket * product.num_priced_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_system_fee(self, pdmp, product_quantities):
        return pdmp.system_fee_per_order + sum([
            (pdmp.system_fee_per_product + \
             pdmp.system_fee_per_ticket * product.num_priced_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_special_fee(self, pdmp, product_quantities):
        return pdmp.special_fee_per_order + sum([
            (pdmp.special_fee_per_product + \
             pdmp.special_fee_per_ticket * product.num_priced_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_products_amount(self, pdmp, product_quantities):
        return sum([
            (product.price + \
             pdmp.per_product_fee + \
             pdmp.per_ticket_fee * product.num_priced_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def applicable(self, user=None, now=None, type='available'):
        return build_sales_segment_query(sales_segment_id=self.id, user=user, now=now, type=type).exists()

class OrganizationSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "OrganizationSetting"
    id = Column(Identifier, primary_key=True)
    DEFAULT_NAME = u"default"
    name = Column(Unicode(255), default=DEFAULT_NAME)
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='settings')

    auth_type = Column(Unicode(255))
    performance_selector = Column(Unicode(255), doc=u"カートでの公演絞り込み方法")
    margin_ratio = Column(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0')
    refund_ratio = Column(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0')
    printing_fee = Column(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0')
    registration_fee = Column(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0')

    multicheckout_shop_name = Column(Unicode(255), unique=True)
    multicheckout_shop_id = Column(Unicode(255))
    multicheckout_auth_id = Column(Unicode(255))
    multicheckout_auth_password = Column(Unicode(255))

    cart_item_name = Column(Unicode(255))

    contact_pc_url = Column(Unicode(255))
    contact_mobile_url = Column(Unicode(255))

    point_type = Column(Integer, nullable=True)
    point_fixed = Column(Numeric(precision=16, scale=2), nullable=True)
    point_rate = Column(Float, nullable=True)

    bcc_recipient = Column(Unicode(255), nullable=True)

class PerformanceSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "PerformanceSetting"
    id = Column(Identifier, primary_key=True)
    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref='settings')
               
    KEYS = []

    @classmethod
    def create_from_model(cls, obj, params):
        kwargs = {k:params.get(k) for k in cls.KEYS}
        settings = cls(**kwargs)
        settings.performance = obj
        return settings

    @classmethod
    def update_from_model(cls, obj, params):
        setting = obj.setting or cls()

        for k in cls.KEYS:
            setattr(setting, k, params.get(k) or "")
        setting.performance = obj
        return setting

    def describe_iter(self):
        columns = self.__mapper__.c
        for k in self.KEYS:
            col = getattr(columns, k, None)
            if col is None:
                yield k, getattr(self, k, None) or u"", k
            else:
                yield k, getattr(self, k, None) or u"", getattr(col, "doc", k) or k

    @classmethod
    def create_from_template(cls, template, **kwargs):
        setting = cls.clone(template)
        return setting


class ImportStatusEnum(StandardEnum):
    Waiting = (1, u'インポート待ち')
    Importing = (2, u'インポート中')
    Imported = (3, u'インポート完了')


class OrderImportTask(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderImportTask'

    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=False)
    performance_id = Column(Identifier, ForeignKey('Performance.id'), nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), nullable=False)
    import_type = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    data = Column(UnicodeText(8388608))
    errors = Column(MutationDict.as_mutable(JSONEncodedDict(65536)), nullable=True)

    organization = relationship('Organization')
    performance = relationship('Performance')
    operator = relationship('Operator')

    @classmethod
    def status_label(cls, status):
        for e in ImportStatusEnum:
            if e.v[0] == status:
                return e.v[1]
        return u''
