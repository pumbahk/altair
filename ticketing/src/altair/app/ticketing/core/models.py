# encoding: utf-8
import logging
import itertools
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
from sqlalchemy.orm import join, backref, column_property, joinedload, deferred, relationship, aliased, undefer
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import asc, desc, exists, select, table, column, case, null, alias, or_
from sqlalchemy.ext.associationproxy import association_proxy
from zope.interface import implementer
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _

from zope.deprecation import deprecation

from .exceptions import InvalidStockStateError, InvalidRefundStateError
from .interfaces import (
    ISalesSegmentQueryable,
    IOrderQueryable,
    IOrderLike,
    IOrderedProductLike,
    IOrderedProductItemLike,
    ISetting,
    ISettingContainer,
    IChainedSetting,
    IAllAppliedSetting
)

from altair.app.ticketing.models import (
    Base, DBSession,
    MutationDict, JSONEncodedDict,
    LogicallyDeleted, Identifier, DomainConstraintError,
    WithTimestamp, BaseModel,
    is_any_of
)

from standardenum import StandardEnum
from altair.app.ticketing.users.models import User, UserCredential, MemberGroup, MemberGroup_SalesSegment
from altair.app.ticketing.utils import tristate, is_nonmobile_email_address, sensible_alnum_decode, todate, todatetime, memoize
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.sej import userside_api
from altair.app.ticketing.sej.interfaces import ISejTenant
from altair.app.ticketing.sej.exceptions import SejError
from altair.app.ticketing.venues.interfaces import ITentativeVenueSite
from .utils import ApplicableTicketsProducer
from . import api

logger = logging.getLogger(__name__)

DEFAULT_PERFORMANCE_SELECTOR = 'date'

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
    zip = Column(Unicode(32))
    prefecture   = Column(Unicode(64), nullable=False, default=u'')
    city = Column(Unicode(255))
    address_1 = Column('street', Unicode(255))
    address_2 = Column('other_address', Unicode(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))
    _drawing_url = Column('drawing_url', String(255))
    _frontend_metadata_url = Column('metadata_url', String(255))
    _backend_metadata_url = Column('backend_metadata_url', String(255))

class L0Seat(Base, BaseModel):
    __tablename__  = 'L0Seat'
    site_id = Column(Identifier, ForeignKey('Site.id', ondelete='CASCADE'), nullable=False)
    l0_id       = Column(Unicode(48), nullable=False)
    row_l0_id   = Column(Unicode(48), nullable=True)
    group_l0_id = Column(Unicode(48), nullable=True)
    name        = Column(Unicode(48), nullable=False, default=u'', server_default='')
    seat_no     = Column(Unicode(50), nullable=True)
    row_no      = Column(Unicode(50), nullable=True)
    block_name  = Column(Unicode(50), nullable=True)
    floor_name  = Column(Unicode(50), nullable=True)
    gate_name   = Column(Unicode(50), nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint(site_id, l0_id),
        )

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
    name = AnnotatedColumn(String(255), _a_label=_(u"会場名"))
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

    def accept_core_model_traverser(self, traverser):
        traverser.begin_venue(self)
        for seat_index_type in self.seat_index_types:
            seat_index_type.accept_core_model_traverser(traverser)
        for area in self.areas:
            area.accept_core_model_traverser(traverser)
        for seat in self.seats:
            seat.accept_core_model_traverser(traverser)
        traverser.end_venue(self)


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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_venue_area(self)


class SeatAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "SeatAttribute"
    seat_id         = Column(Identifier, ForeignKey('Seat.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    name            = Column(String(255), primary_key=True, nullable=False)
    value           = Column(String(1023))

    def accept_core_model_traverser(self, traverser):
        traverser.visit_seat_attribute(self)


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
    def query_sales_seats(cls, sales_segment, session=None):
        session = session or DBSession
        return session.query(cls).filter(
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

    def accept_core_model_traverser(self, traverser):
        traverser.begin_seat(self)
        for attribute in self.attributes_.values():
            attribute.accept_core_model_traverser(traverser)
        for seat_index in self.indexes:
            seat_index.accept_core_model_traverser(traverser)
        traverser.end_seat(self)

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

class SeatGroup(Base, BaseModel):
    __tablename__ = "SeatGroup"
    __table_args__ = (
        UniqueConstraint('site_id', 'l0_id', name='ix_SeatGroup_site_id_l0_id'),
        )
    query = DBSession.query_property()
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    name = Column(Unicode(50), nullable=False, default=u"", server_default=u"")
    site_id = Column(Identifier, ForeignKey("Site.id"), nullable=False)
    l0_id = Column(Unicode(48), nullable=False, index=True)

    site = relationship("Site", backref="seat_groups")

    def query_seats_for_venue(self, venue):
        cls = self.__class__
        session = object_session(self)
        return session.query(Seat) \
            .filter(self.l0_id == Seat.row_l0_id, Seat.venue_id == venue.id) \
            .union(
                session.query(Seat) \
                .filter(self.l0_id == Seat.group_l0_id, Seat.venue_id == venue.id))

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

@implementer(ISalesSegmentQueryable, IOrderQueryable, ISettingContainer)
class Performance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Performance'

    id = Column(Identifier, primary_key=True)
    name = AnnotatedColumn(String(255), _a_label=_(u'名称'))
    # see #2042
    # 旧仕様: Event.code(5桁) + 7桁(デフォルトはstart.onのYYMMDD+ランダム1桁)
    # 新仕様: Event.code(7桁) + 5桁(デフォルトはstart.onのMMDD+ランダム1桁)
    code = Column(String(12))
    abbreviated_title = Column(Unicode(255), doc=u"公演名略称", default=u"")
    subtitle = Column(Unicode(255), doc=u"公演名副題", default=u"")
    note = Column(UnicodeText, doc=u"公演名備考", default=u"")

    open_on = AnnotatedColumn(DateTime, _a_label=_(u"開場"))
    start_on = AnnotatedColumn(DateTime, _a_label=_(u"開演")) # 必須
    end_on = AnnotatedColumn(DateTime, _a_label=_(u"終了"))
    public = Column(Boolean, nullable=False, default=False)  # 一般公開するか

    event_id = Column(Identifier, ForeignKey('Event.id'))

    stocks = relationship('Stock', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    venue = relationship('Venue', uselist=False, backref='performance')

    redirect_url_pc = Column(String(1024))
    redirect_url_mobile = Column(String(1024))

    display_order = AnnotatedColumn(Integer, nullable=False, default=1, _a_label=_(u'表示順'))

    setting = relationship('PerformanceSetting', backref='performance', uselist=False, cascade='all')

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
            - SalesSegmentSetting
            - Product
              - ProductItem
            − MemberGroup_SalesSegment
          - Stock
            - StockStatus
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
            if template_performance.setting:
                setting = template_performance.setting
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

        # 相対日付の再計算
        for sales_segment in self.sales_segments:
            if sales_segment.use_default_start_at:
                sales_segment.start_at = sales_segment.sales_segment_group.start_for_performance(sales_segment.performance)
            if sales_segment.use_default_end_at:
                sales_segment.end_at = sales_segment.sales_segment_group.end_for_performance(sales_segment.performance)

    def delete(self):

        if self.public:
            raise Exception(u'公開中の為、削除できません')

        if len(self.orders) > 0:
            raise Exception(u'購入されている為、削除できません')

        if len(self.product_items) > 0:
            raise Exception(u'商品詳細がある為、削除できません')

        allocation = Stock.query.filter(
            Stock.performance_id==self.id,
            Stock.stock_holder_id!=None
            ).with_entities(func.sum(Stock.quantity)).scalar()

        if allocation > 0:
            raise Exception(u'配席されている為、削除できません')

        lot_products = Product.query.join(Product.sales_segment).filter(
            Product.performance_id==self.id,
            SalesSegment.performance_id==None
            ).count()

        if lot_products > 0:
            raise Exception(u'抽選商品がある為、削除できません')

        # delete PerformanceSetting
        if self.setting:
            self.setting.delete()

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
        sales_segments = DBSession.query(SalesSegment, include_deleted=True).options(undefer(SalesSegment.deleted_at), joinedload(SalesSegment.sales_segment_group)).filter_by(performance_id=self.id).all()

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

    def query_orders_by_user(self, user, filter_canceled=False, query=None):
        """ 該当ユーザーがこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query \
            .join(Order.sales_segment) \
            .filter(Order.user_id == user.id) \
            .filter(SalesSegment.performance_id == self.id)
        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs

    def query_orders_by_mailaddresses(self, mailaddresses, filter_canceled=False, query=None):
        """ 該当メールアドレスによるこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query \
            .join(Order.shipping_address) \
            .join(Order.sales_segment) \
            .filter(
                or_(ShippingAddress.email_1.in_(mailaddresses),
                    ShippingAddress.email_2.in_(mailaddresses))
                ) \
            .filter(SalesSegment.performance_id == self.id)
        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs


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
            if len(event.code) == 7:
                # 新仕様
                performance.code = event.code + performance.code[7:]
            elif len(event.code) == 5:
                # 旧仕様
                performance.code = event.code + performance.code[5:]
            else:
                raise ValueError("Invalid event code length: event_id=%d, code=%s" % (event.id, event.code))
            assert len(performance.code) == 12
        performance.original_id = template.id
        performance.venue_id = template.venue.id
        performance.create_venue_id = template.venue.id
        performance.save()
        logger.info('[copy] Performance end')
        return {template.id: performance.id}

    def has_that_delivery(self, delivery_plugin_id):
        qs = DBSession.query(DeliveryMethod)\
            .filter(DeliveryMethod.delivery_plugin_id==delivery_plugin_id)\
            .filter(DeliveryMethod.id==PaymentDeliveryMethodPair.delivery_method_id)\
            .filter(PaymentDeliveryMethodPair.sales_segment_group_id == SalesSegment.id)\
            .filter(SalesSegment.id==Product.sales_segment_group_id)\
            .filter(Product.id==ProductItem.product_id)\
            .filter(ProductItem.performance_id==self.id)
        return bool(qs.first())

    def accept_core_model_traverser(self, traverser):
        traverser.begin_performance(self)
        if self.setting is not None:
            traverser.visit_performance_setting(self.setting)
        for stock in self.stocks:
            stock.accept_core_model_traverser(traverser)
        self.venue.accept_core_model_traverser(traverser)
        traverser.end_performance(self)

class ReportFrequencyEnum(StandardEnum):
    Daily = (1, u'毎日')
    Weekly = (2, u'毎週')
    Onetime = (3, u'1回のみ')

class ReportPeriodEnum(StandardEnum):
    Normal = (1, u'指定期間 (前日分/前週分)')
    Entire = (2, u'全期間 (販売開始〜送信日時まで)')

class ReportTypeEnum(StandardEnum):
    Detail = (1, u'詳細 (販売区分別まで含む)')
    Summary = (2, u'合計 (公演合計のみ)')

class ReportSetting_ReportRecipient(Base):
    __tablename__   = 'ReportSetting_ReportRecipient'
    report_setting_id = Column(Identifier, ForeignKey('ReportSetting.id', ondelete='CASCADE'), primary_key=True)
    report_recipient_id = Column(Identifier, ForeignKey('ReportRecipient.id', ondelete='CASCADE'), primary_key=True)

class ReportRecipient(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = 'ReportRecipient'
    id = Column(Identifier(), primary_key=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=False)
    organization = relationship('Organization', backref='report_recipients')

    def format_recipient(self):
        return u'{0} <{1}>'.format(self.name, self.email)

class ReportSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = 'ReportSetting'
    id = Column(Identifier, primary_key=True)
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'), nullable=True)
    event = relationship('Event', backref='report_settings')
    performance_id = Column(Identifier, ForeignKey('Performance.id', ondelete='CASCADE'), nullable=True)
    performance = relationship('Performance', backref='report_settings')
    frequency = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    time = Column(String(4), nullable=False)
    day_of_week = Column(Integer, nullable=True, default=None)
    start_on = Column(DateTime, nullable=True, default=None)
    end_on = Column(DateTime, nullable=True, default=None)
    report_type = Column(Integer, nullable=False, default=1, server_default='1')
    recipients = relationship('ReportRecipient', secondary=ReportSetting_ReportRecipient.__table__, backref='settings')

    def format_recipients(self):
        return u', '.join([r.format_recipient() for r in self.recipients])

    def format_emails(self):
        return u', '.join([r.email for r in self.recipients])

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

    if user and (user.get('is_guest') or user.get('membership') == 'rakuten'):
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

@implementer(ISalesSegmentQueryable, IOrderQueryable, ISettingContainer)
class Event(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Event'

    id = Column(Identifier, primary_key=True)
    # see #2042
    # 旧仕様: Organization.code(2桁) + 3桁の英数字
    # 新仕様: Organization.code(2桁) + 5桁の英数字
    code = Column(String(12))
    title = AnnotatedColumn(String(1024), _a_label=_(u'イベント名称'))
    abbreviated_title = AnnotatedColumn(String(1024), _a_label=_(u'イベント略称'))

    account_id = AnnotatedColumn(Identifier, ForeignKey('Account.id'), _a_label=_(u'配券元'))
    account = relationship('Account', backref='events')

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='events')

    performances = relationship('Performance', backref='event', order_by='Performance.start_on')
    stock_types = relationship('StockType', backref='event', order_by='StockType.display_order')
    stock_holders = relationship('StockHolder', backref='event')

    sales_segment_groups = relationship('SalesSegmentGroup')
    cms_send_at = Column(DateTime, nullable=True, default=None)

    display_order = AnnotatedColumn(Integer, nullable=False, default=1, _a_label=_(u'表示順'))

    setting = relationship('EventSetting', backref='event', uselist=False, cascade='all')

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
        performances = DBSession.query(Performance, include_deleted=True).options(undefer(Performance.deleted_at)).filter_by(event_id=self.id).all()
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
              - EventSetting
              - Lot
            """
            template_event = Event.get(self.original_id)

            # 各モデルのコピー元/コピー先のidの対比表
            convert_map = {
                'performance': dict(),
                'stock_type': dict(),
                'stock_holder': dict(),
                'sales_segment_group': dict(),
                'product': dict(),
                'product_item': dict(),
                'ticket': dict(),
                'ticket_bundle': dict(),
                'sales_segment': dict(),
                'lot': dict(),
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
                convert_map['performance'].update(
                    Performance.create_from_template(template=template_performance, event_id=self.id)
                    )

            # create EventSettings
            if template_event.setting:
                setting = template_event.setting
                EventSetting.create_from_template(template=setting, event_id=self.id)

            for key, src_dst in convert_map.items():
                for src, dst in src_dst.items():
                    logger.info('[COPY] CONVERT: {}: {} -> {}'.format(key, src, dst))
            # create Lot
            for lot_src in template_event.lots:

                ssg_src = lot_src.sales_segment.sales_segment_group
                ssg_id = convert_map['sales_segment_group'][ssg_src.id]
                ss_src = lot_src.sales_segment
                res = SalesSegment.create_from_template(ss_src, sales_segment_group_id=ssg_id)
                convert_map['sales_segment'].update(res)

                lot = lot_src.create_from_template(
                    lot_src,
                    event_id=self.id,
                    sales_segment_id=convert_map['sales_segment'][ss_src.id],
                    )
                convert_map['lot'][lot_src.id] = lot.id
                logger.info('[COPY] Lot id={}'.format(lot.id))

                for prod_src in ss_src.products:

                    res = Product.create_from_template(
                        prod_src,
                        with_product_items=False,
                        event_id=self.id,
                        performance_id=convert_map['performance'][prod_src.performance_id],
                        **convert_map
                        )
                    convert_map['product'].update(res)
                    logger.info('[COPY] Lot Product id = {}'.format(res))
                    for pitem_src in ProductItem.query.filter(ProductItem.product_id == prod_src.id):
                        res = ProductItem.create_from_template_for_lot(
                            pitem_src,
                            product_id=convert_map['product'][prod_src.id],
                            performance_id=convert_map['performance'][pitem_src.stock.performance_id],
                            sales_segment_id=convert_map['sales_segment'][prod_src.sales_segment_id],
                            )
                        convert_map['product_item'].update(res)
                        pitem_id = res.values()[0]
                        pitem_dst = ProductItem.get(id=pitem_id)
                        pitem_dst.save()

            for key, src_dst in convert_map.items():
                for src, dst in src_dst.items():
                    logger.info('[COPY] LOT COPIED: {}: {} -> {}'.format(key, src, dst))

            # other
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
            # コピーされた販売区分グループの持つ販売区分のmembergroupに propagate する必要がある (refs #7784)
            for sales_segment_group_id in convert_map['sales_segment_group'].values():
                sales_segment_group = SalesSegmentGroup.query.filter_by(id=sales_segment_group_id).one()
                sales_segment_group.sync_member_group_to_children()
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

    def query_orders_by_user(self, user, filter_canceled=False, query=None):
        """ 該当ユーザーがこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query \
            .join(Order.sales_segment) \
            .filter(Order.user_id == user.id) \
            .filter(SalesSegment.event_id == self.id)
        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs

    def query_orders_by_mailaddresses(self, mailaddresses, filter_canceled=False, query=None):
        """ 該当メールアドレスによるこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query \
            .join(Order.shipping_address) \
            .join(Order.sales_segment) \
            .filter(
                or_(ShippingAddress.email_1.in_(mailaddresses),
                    ShippingAddress.email_2.in_(mailaddresses))
                ) \
            .filter(SalesSegment.event_id == self.id)
        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs

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

    @property
    def performance_selector(self):
        event_setting = self.setting
        if event_setting is not None and event_setting.cart_setting is not None and event_setting.cart_setting.performance_selector:
            return event_setting.cart_setting.performance_selector
        organization_setting = self.organization.setting
        if organization_setting is not None and organization_setting.cart_setting is not None and organization_setting.cart_setting.performance_selector:
            return organization_setting.cart_setting.performance_selector
        return DEFAULT_PERFORMANCE_SELECTOR

    def sorted_performances(self):
        return sorted(self.performances, key=lambda p: (p.display_order, p.id))

    def accept_core_model_traverser(self, traverser):
        traverser.begin_event(self)
        if self.setting is not None:
            traverser.visit_event_setting(self.setting)
        for stock_type in self.stock_types:
            stock_type.accept_core_model_traverser(traverser)
        for stock_holder in self.stock_holders:
            stock_holder.accept_core_model_traverser(traverser)
        for ticket in self.tickets:
            ticket.accept_core_model_traverser(traverser)
        for ticket_bundle in self.ticket_bundles:
            ticket_bundle.accept_core_model_traverser(traverser)
        for performance in self.performances:
            performance.accept_core_model_traverser(traverser)
        for sales_segment_group in self.sales_segment_groups:
            sales_segment_group.accept_core_model_traverser(traverser)
        for lot in self.lots:
            lot.accept_core_model_traverser(traverser)
        traverser.end_event(self)

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
    max_quantity = AnnotatedColumn('upper_limit', Integer, _a_label=_(u'購入上限枚数'))
    order_limit = association_proxy('setting', 'order_limit', creator=lambda order_limit: SalesSegmentGroupSetting(order_limit=order_limit))
    max_product_quatity = AnnotatedColumn('product_limit', Integer, _a_label=_(u'商品購入上限数'))

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
    auth3d_notice = AnnotatedColumn(UnicodeText, _a_label=_(u'クレジットカード 3D認証フォーム 注記事項'))

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref="sales_segment_group")

    start_day_prior_to_performance = Column(Integer)
    start_time = Column(Time)
    end_day_prior_to_performance = Column(Integer)
    end_time = Column(Time)

    setting = relationship('SalesSegmentGroupSetting', uselist=False, backref='sales_segment_group', cascade='all', lazy='joined')

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
        return SalesSegment(
            sales_segment_group=self,
            event=self.event,
            organization=self.organization,
            membergroups=list(self.membergroups),
            setting=SalesSegmentSetting()
            )

    @staticmethod
    def create_from_template(template, with_payment_delivery_method_pairs=False, **kwargs):
        sales_segment_group = SalesSegmentGroup.clone(template)
        if template.setting is not None:
            sales_segment_group.setting = SalesSegmentGroupSetting.create_from_template(template.setting)
        if 'event_id' in kwargs:
            sales_segment_group.event_id = kwargs['event_id']
        sales_segment_group.membergroups = list(template.membergroups)
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

    def accept_core_model_traverser(self, traverser):
        traverser.begin_sales_segment_group(self)
        if self.setting is not None:
            traverser.visit_sales_segment_group_setting(self.setting)
        for payment_delivery_method_pair in self.payment_delivery_method_pairs:
            payment_delivery_method_pair.accept_core_model_traverser(traverser)
        for sales_segment in self.sales_segments:
            sales_segment.accept_core_model_traverser(traverser)
        traverser.end_sales_segment_group(self)


SalesSegment_PaymentDeliveryMethodPair = Table(
    "SalesSegment_PaymentDeliveryMethodPair",
    Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('payment_delivery_method_pair_id', Identifier, ForeignKey('PaymentDeliveryMethodPair.id')),
    Column('sales_segment_id', Identifier, ForeignKey('SalesSegment.id')),
    )

class DateCalculationBase(StandardEnum):
    Absolute             = 0
    OrderDate            = 1
    PerformanceStartDate = 2
    PerformanceEndDate   = 3
    SalesStartDate       = 4
    SalesEndDate         = 5
    OrderDateTime        = 6

class DateCalculationBias(StandardEnum):
    Exact       = 0
    StartOfDay  = 1
    EndOfDay    = 2

def get_base_datetime_from_order_like(order_like, base_type):
    if base_type == DateCalculationBase.Absolute.v:
        return None
    elif base_type == DateCalculationBase.OrderDate.v:
        return order_like.created_at # TODO: created_at is not part of IOrderLike interface
    elif base_type == DateCalculationBase.OrderDateTime.v:
        return order_like.created_at
    elif base_type == DateCalculationBase.PerformanceStartDate.v:
        performance = order_like.performance
        return performance and performance.start_on
    elif base_type == DateCalculationBase.PerformanceEndDate.v:
        performance = order_like.performance
        return performance and (performance.end_on or performance.start_on.replace(hour=23, minute=59, second=59))
    elif base_type == DateCalculationBase.SalesStartDate.v:
        return order_like.sales_segment.start_at
    elif base_type == DateCalculationBase.SalesEndDate.v:
        return order_like.sales_segment.end_at or order_like.created_at.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=365, second=-1)

def calculate_date_from_order_like(order_like, base_type, bias, period, abs_date):
    if base_type == DateCalculationBase.Absolute.v:
        assert period is None or period == 0, 'Should no be specified period when specified absolute. There is a possibility that the data migration has failed.'
        return abs_date
    elif base_type == DateCalculationBase.OrderDateTime.v:
        if period is None:
            raise ValueError('period must be specified if base_type is not Absolute')
        base = get_base_datetime_from_order_like(order_like, base_type)
        if base is None:
            raise ValueError('could not determine base date')
        return base + timedelta(days=period)
    else:
        if period is None:
            raise ValueError('period must be specified if base_type is not Absolute')
        base = get_base_datetime_from_order_like(order_like, base_type)
        if base is None:
            raise ValueError('could not determine base date')

        if bias == DateCalculationBias.StartOfDay.v:
            base = base.replace(hour=0, minute=0, second=0, microsecond=0)
        elif bias == DateCalculationBias.EndOfDay.v:
            base = base.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, seconds=-1)
        return base + timedelta(days=period)

class PaymentDeliveryMethodPair(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentDeliveryMethodPair'
    query = DBSession.query_property()
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))

    system_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'システム利用料'))
    system_fee_type = AnnotatedColumn(Integer, nullable=False, default=FeeTypeEnum.Once.v[0], _a_label=_(u'システム利用料計算単位'))

    transaction_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'決済手数料'))
    _delivery_fee = AnnotatedColumn('delivery_fee', Numeric(precision=16, scale=2), nullable=True, _a_label=_(u'引取手数料'))
    delivery_fee_per_order = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'引取手数料 (予約ごと)'))
    delivery_fee_per_principal_ticket = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'引取手数料 (主券)'))
    delivery_fee_per_subticket = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'引取手数料 (副券)'))
    discount = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=_(u'割引額'))
    discount_unit = AnnotatedColumn(Integer, _a_label=_(u'割引数'))

    # 支払開始日時
    payment_start_day_calculation_base = AnnotatedColumn(Integer, nullable=False, default=DateCalculationBase.OrderDate.v, server_default=str(DateCalculationBase.OrderDate.v), _a_label=_(u'支払開始日時の計算基準'))
    payment_start_in_days = AnnotatedColumn(Integer, default=0, _a_label=_(u'コンビニでの支払開始までの日数'))
    payment_start_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'支払開始日時'))

    # 支払期限
    payment_due_day_calculation_base = AnnotatedColumn(Integer, nullable=False, default=DateCalculationBase.OrderDate.v, server_default=str(DateCalculationBase.OrderDate.v), _a_label=_(u'支払期限日時の計算基準'))
    payment_period_days = AnnotatedColumn(Integer, nullable=True, _a_label=_(u'コンビニでの支払期限日数'))
    payment_due_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'支払期日'))

    # 発券開始日時
    issuing_start_day_calculation_base = AnnotatedColumn(Integer, nullable=False, default=DateCalculationBase.OrderDate.v, server_default=str(DateCalculationBase.OrderDate.v), _a_label=_(u'発券開始日時の計算基準'))
    issuing_interval_days = AnnotatedColumn(Integer, nullable=True, _a_label=_(u'コンビニでの発券が可能となるまでの日数'))
    issuing_start_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'コンビニ発券開始日時'))

    # 発券終了日時
    issuing_end_day_calculation_base = AnnotatedColumn(Integer, nullable=False, default=DateCalculationBase.OrderDate.v, server_default=str(DateCalculationBase.OrderDate.v), _a_label=_(u'発券開始日時の計算基準'))
    issuing_end_in_days = AnnotatedColumn(Integer, nullable=True, _a_label=_(u'コンビニでの発券終了までの日数'))
    issuing_end_at = AnnotatedColumn(DateTime, nullable=True, _a_label=_(u'コンビニ発券期限日時'))

    # 選択不可期間 (SalesSegment.end_atの何日前から利用できないか、日数指定)
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
    special_fee_type = AnnotatedColumn(Integer, nullable=False, default=FeeTypeEnum.Once.v[0], _a_label=_(u'特別手数料計算単位'))

    @property
    def delivery_fee_per_product(self):
        """商品ごとの引取手数料"""
        return Decimal()

    @property
    def delivery_fee(self):
        warn_deprecated("deprecated attribute `delivery_fee' is accessed")
        if self.delivery_fee_per_order:
            if self.delivery_fee_per_principal_ticket:
                raise Exception('both delivery_fee_per_order and delivery_fee_per_ticket are non-zero')
            else:
                return self.delivery_fee_per_order
        else:
            return self.delivery_fee_per_principal_ticket

    @property
    def delivery_fee_per_ticket(self):
        warn_deprecated("deprecated attribute `delivery_fee_per_ticket' is accessed")
        return self.delivery_fee_per_principal_ticket

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
    def per_ticket_fee_excluding_delivery_fee(self):
        return self.system_fee_per_ticket + self.special_fee_per_ticket + self.transaction_fee_per_ticket

    @property
    def per_ticket_fee(self):
        warn_deprecated("deprecated attribute `per_ticket_fee' is accessed")
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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_payment_delivery_method_pair(self)


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
    name = Column(Unicode(255))
    description = Column(Unicode(2000))
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

    def pay_at_store(self):
        """
        コンビニ支払かどうかを判定する。
        """
        return self.payment_plugin_id == plugins.SEJ_PAYMENT_PLUGIN_ID


class DeliveryMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethod'
    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=_(u'ID'))
    name = AnnotatedColumn(Unicode(255), _a_label=_(u'表示名称'))
    description = AnnotatedColumn(Unicode(2000), _a_label=_(u'説明文 (HTML)'))
    _fee = Column('fee', Numeric(precision=16, scale=2), nullable=True)
    _fee_type = Column('fee_type', Integer, nullable=True, default=FeeTypeEnum.Once.v[0])

    fee_per_order = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'手数料 (予約ごと)'))
    fee_per_principal_ticket = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'手数料 (主券)'))
    fee_per_subticket = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=Decimal('0.00'), _a_label=_(u'手数料 (副券)'))

    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), _a_label=_(u'オーガニゼーション'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')

    delivery_plugin_id = AnnotatedColumn(Identifier, ForeignKey('DeliveryMethodPlugin.id'), _a_label=_(u'引取方法'))
    _delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)


    # 引換票を表示しないオプション（SEJ専用）
    hide_voucher = AnnotatedColumn(Boolean, default=False, _a_label=_(u'引換票を表示しない'))

    @property
    def fee(self):
        if self.fee_per_order:
            if self.fee_per_principal_ticket:
                raise Exception('both fee_per_order and fee_per_ticket are non-zero')
            else:
                return self.fee_per_order
        else:
            return self.fee_per_principal_ticket

    @property
    def fee_type(self):
        if self.fee_per_order:
            if self.fee_per_principal_ticket:
                raise Exception('both fee_per_order and fee_per_ticket are non-zero')
            else:
                return FeeTypeEnum.Once.v[0]
        else:
            return FeeTypeEnum.PerUnit.v[0]

    @property
    def fee(self):
        if self.fee_per_order:
            if self.fee_per_principal_ticket:
                raise Exception('both fee_per_order and fee_per_ticket are non-zero')
            else:
                return self.fee_per_order
        else:
            return self.fee_per_principal_ticket

    @property
    def fee_type(self):
        if self.fee_per_order:
            if self.fee_per_principal_ticket:
                raise Exception('both fee_per_order and fee_per_ticket are non-zero')
            else:
                return FeeTypeEnum.Once.v[0]
        else:
            return FeeTypeEnum.PerUnit.v[0]

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

    def deliver_at_store(self):
        """
        コンビニ受取かどうかを判定する。
        """
        return self.delivery_plugin_id == plugins.SEJ_DELIVERY_PLUGIN_ID

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
    def _create_from_template(template, **kwargs):
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
        return {template.id: product_item.id}


    @staticmethod
    def create_from_template_for_lot(*args, **kwds):
        return ProductItem._create_from_template(*args, **kwds)

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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_product_item(self)


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
    disp_reports = Column(Boolean, default=True)
    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))
    description=Column(Unicode(2000), nullable=True, default=None)
    stocks = relationship('Stock', backref=backref('stock_type', order_by='StockType.display_order'))
    min_quantity = Column(Integer, nullable=True, default=None)
    max_quantity = Column(Integer, nullable=True, default=None)
    min_product_quantity = Column(Integer, nullable=True, default=None)
    max_product_quantity = Column(Integer, nullable=True, default=None)

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

    def add(self):
        super(StockType, self).add()

        # create default Stock
        Stock.create_default(self.event, stock_type_id=self.id)

    def update_stock_types(self, old_display_order):
        min_display_order = 1
        max_display_order = len(StockType.query.filter(StockType.event_id==self.event_id).all())
        if self.display_order < min_display_order:
            self.display_order = min_display_order
        if self.display_order > max_display_order:
            self.display_order = max_display_order

        if old_display_order > self.display_order:
            stock_types = StockType.query.filter(StockType.event_id==self.event_id)\
                .filter(StockType.id!=self.id)\
                .filter(StockType.display_order>=self.display_order)\
                .filter(StockType.display_order<old_display_order).all()

            for st in stock_types:
                st.display_order += 1
                st.save()

        if old_display_order < self.display_order:
            stock_types = StockType.query.filter(StockType.event_id==self.event_id)\
                .filter(StockType.id!=self.id)\
                .filter(StockType.display_order<=self.display_order)\
                .filter(StockType.display_order>=old_display_order).all()

            for st in stock_types:
                st.display_order -= 1
                st.save()

        self.save()

    def delete(self):
        stock_types = StockType.query.filter(StockType.event_id==self.event_id)\
            .filter(StockType.display_order>self.display_order).all()

        for stock_type in stock_types:
            stock_type.display_order -= 1
            stock_type.save()

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

    def init_display_order(self, event_id):
        types = StockType.query.filter(StockType.event_id==event_id).all()
        self.display_order = len(types) + 1

    def init_style(self, data):
        if self.is_seat:

            self.style = {
                'stroke':{
                    'color':data.get('stroke_color'),
                    'width':data.get('stroke_width'),
                    'pattern':data.get('stroke_patten'),
                },
                'fill':{
                    'color':self.get_fill_color(self.display_order-1),
                },
            }
        else:
            self.style = {}

    def get_fill_color(self, color_no):
        color_dict = ['#ff0000', '#3366ff', '#009900', '#ffff00',
                      '#9900ff', '#80cccc', '#ff80cc', '#cce680']
        return color_dict[color_no % len(color_dict)]

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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_stock_type(self)


class StockHolder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockHolder"
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

    event_id = Column(Identifier, ForeignKey('Event.id'))
    account_id = Column(Identifier, ForeignKey('Account.id'))

    is_putback_target = Column(Boolean, nullable=True) # CooperationTypeEnum

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
        if user_id is not None:
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

    def num_seats(self, performance_id=None, sale_only=False):
        # 同一Performanceの同一StockHolderにおけるStock.quantityの合計
        query = Stock.filter_by(stock_holder_id=self.id).with_entities(func.sum(Stock.quantity))
        if performance_id:
            query = query.filter_by(performance_id=performance_id)
            if sale_only:
                query = query.filter(exists().where(and_(ProductItem.performance_id==performance_id, ProductItem.stock_id==Stock.id)))
        return query.scalar()

    def rest_num_seats(self, performance_id=None, sale_only=False):
        # 同一Performanceの同一StockHolderにおけるStockStatus.quantityの合計
        query = Stock.filter(Stock.stock_holder_id==self.id).join(Stock.stock_status).with_entities(func.sum(StockStatus.quantity))
        if performance_id:
            query = query.filter(Stock.performance_id==performance_id)
            if sale_only:
                query = query.filter(exists().where(and_(ProductItem.performance_id==performance_id, ProductItem.stock_id==Stock.id)))
        return query.scalar()

    def accept_core_model_traverser(self, traverser):
        traverser.visit_stock_holder(self)


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
            from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
            from altair.app.ticketing.cart.models import CartedProduct, CartedProductItem
            # 販売済みの座席数
            reserved_quantity = Stock.filter(Stock.id==self.id).join(Stock.product_items)\
                .join(ProductItem.ordered_product_items)\
                .join(OrderedProductItem.ordered_product)\
                .join(OrderedProduct.order)\
                .filter(Order.canceled_at==None, Order.refunded_at==None)\
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
                if Stock.query.filter(
                    Stock.performance_id == performance.id,
                    Stock.stock_type_id == stock_type.id) \
                    .with_entities(Stock.id).first() is None:
                    stock = Stock(
                        performance_id=performance.id,
                        stock_type_id=stock_type.id,
                        stock_holder_id=None,
                        quantity=0
                    )
                    stock.save()

                # Performance × StockType × StockHolder分のStockを生成
                for stock_holder in stock_holders:
                    if Stock.query.filter(
                        Stock.performance_id == performance.id,
                        Stock.stock_type_id == stock_type.id,
                        Stock.stock_holder_id == stock_holder.id) \
                        .with_entities(Stock.id).first() is None:
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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_stock(self)

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
    must = AnnotatedColumn(Boolean, nullable=False, default=False, _a_label=_(u'必須'))

    description = Column(Unicode(2000), nullable=True, default=None)

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref='products')

    stocks = association_proxy('items', 'stock')
    base_product_id = Column(Identifier, nullable=True)

    min_product_quantity = Column(Integer, nullable=True)
    max_product_quantity = Column(Integer, nullable=True)

    augus_ticket_id = Column(Identifier, ForeignKey('AugusTicket.id'), nullable=True)
    augus_ticket = relationship('AugusTicket', backref='products')

    @staticmethod
    def find(performance_id=None, event_id=None, sales_segment_group_id=None, stock_id=None, include_deleted=False):
        query = DBSession.query(Product, include_deleted=include_deleted)
        if performance_id:
            query = query.join(Product.items).filter(ProductItem.performance_id==performance_id)
        if event_id:
            query = query.filter(Product.event_id==event_id)
        if sales_segment_group_id:
            query = query.filter(Product.sales_segment_group_id==sales_segment_group_id)
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

    def get_quantity_power(self, stock_type=None, performance_id=None):
        """ 数量倍率 """
        query = ProductItem.query \
            .filter(ProductItem.product==self)
        if performance_id is not None:
            query = query.filter(ProductItem.performance_id==performance_id)
        if stock_type is not None:
            query = query.join(ProductItem.stock).filter(Stock.stock_type == stock_type)
        return sum(pi.quantity for pi in query)


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

    @memoize()
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

    @memoize()
    def num_principal_tickets(self, pdmp):
        '''この Product に関わるTicketのうち、手数料を取るもの (額面があるもの)'''
        return DBSession.query(func.sum(ProductItem.quantity)) \
            .filter(Ticket_TicketBundle.ticket_bundle_id == ProductItem.ticket_bundle_id) \
            .filter((Ticket.id == Ticket_TicketBundle.ticket_id) & (Ticket.deleted_at == None)) \
            .filter((ProductItem.product_id == self.id) & (ProductItem.deleted_at == None)) \
            .filter((Ticket.ticket_format_id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat_DeliveryMethod.deleted_at == None)) \
            .filter((TicketFormat.id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat.deleted_at == None)) \
            .filter(TicketFormat_DeliveryMethod.delivery_method_id == pdmp.delivery_method_id) \
            .filter(Ticket.principal == True) \
            .scalar() or 0

    @memoize()
    def num_subtickets(self, pdmp):
        '''この Product に関わるTicketのうち、手数料を基本的に取らないもの (額面がないもの)'''
        return DBSession.query(func.sum(ProductItem.quantity)) \
            .filter(Ticket_TicketBundle.ticket_bundle_id == ProductItem.ticket_bundle_id) \
            .filter((Ticket.id == Ticket_TicketBundle.ticket_id) & (Ticket.deleted_at == None)) \
            .filter((ProductItem.product_id == self.id) & (ProductItem.deleted_at == None)) \
            .filter((Ticket.ticket_format_id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat_DeliveryMethod.deleted_at == None)) \
            .filter((TicketFormat.id == TicketFormat_DeliveryMethod.ticket_format_id) & (TicketFormat.deleted_at == None)) \
            .filter(TicketFormat_DeliveryMethod.delivery_method_id == pdmp.delivery_method_id) \
            .filter(Ticket.principal == False) \
            .scalar() or 0

    def has_order(self):
        for op in self.ordered_products:
            if op.order:
                return True
        return False

    def has_lot_entry_products(self):
        from altair.app.ticketing.lots.models import LotEntryProduct
        return bool(LotEntryProduct.query.filter(LotEntryProduct.product_id==self.id).count())

    def is_amount_mismatching(self):
        return self.price != sum(pi.price * pi.quantity for pi in self.items)

    def accept_core_model_traverser(self, traverser):
        traverser.begin_product(self)
        for product_item in self.items:
            product_item.accept_core_model_traverser(traverser)
        traverser.end_product(self)


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

    def accept_core_model_traverser(self, traverser):
        traverser.visit_seat_index_type(self)


class SeatIndex(Base, BaseModel):
    __tablename__      = "SeatIndex"
    seat_index_type_id = Column(Identifier, ForeignKey('SeatIndexType.id', ondelete='CASCADE'), primary_key=True)
    seat_id            = Column(Identifier, ForeignKey('Seat.id', ondelete='CASCADE'), primary_key=True)
    index              = Column(Integer, nullable=False)
    seat               = relationship('Seat', backref='indexes')

    def accept_core_model_traverser(self, traverser):
        traverser.visit_seat_index(self)

class OrganizationTypeEnum(StandardEnum):
    Standard = 1

@implementer(ISettingContainer)
class Organization(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Organization"
    id = Column(Identifier, primary_key=True)
    name = AnnotatedColumn(String(255), _a_label=u"名称")
    code = AnnotatedColumn(String(3), _a_label=u"組織コード")  # 2桁英字大文字のみ
    short_name = AnnotatedColumn(String(32), nullable=False, index=True, doc=u"templateの出し分けなどに使う e.g. %(short_name)s/index.html",  _a_label=u"識別子")
    client_type = AnnotatedColumn(Integer, _a_label=u"組織種別")
    contact_email = AnnotatedColumn(String(255), _a_label=u"連絡先メールアドレス")
    company_name = AnnotatedColumn(String(255), _a_label=u"会社名")
    section_name = AnnotatedColumn(String(255), _a_label=u"部署名")
    zip = AnnotatedColumn(Unicode(32), _a_label=u"郵便番号")
    prefecture = AnnotatedColumn(Unicode(64), nullable=False, default=u'', _a_label=u"都道府県")
    city = AnnotatedColumn(Unicode(255), _a_label=u"市区町村")
    address_1 = AnnotatedColumn('street', Unicode(255), _a_label=u"町名以下の住所")
    address_2 = AnnotatedColumn('other_address', Unicode(255), _a_label=u"建物名など")
    tel_1 = AnnotatedColumn(String(32), _a_label=u"電話番号1")
    tel_2 = AnnotatedColumn(String(32), _a_label=u"電話番号2")
    fax = AnnotatedColumn(String(32), _a_label=u"FAX番号")
    status = AnnotatedColumn(Integer, _a_label=u"ステータス")

    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship("User", uselist=False, backref=backref('organization', uselist=False))

    _setting = None

    def get_setting(self, name):
        settings = getattr(self, 'settings', None)
        if settings is not None:
            for setting in settings:
                if setting.name == name:
                    break
            else:
                setting = None
        else:
            setting = object_session(self).query(OrganizationSetting).filter_by(organization_id=self.id, name=name).first()
        if setting is None:
            raise Exception("organization; id={0} does not have {1} setting".format(self.id, name))
        return setting

    @property
    def setting(self):
        if self._setting is not None:
            return self._setting
        self._setting = setting = self.get_setting(u'default')
        return self._setting

    @property
    def point_feature_enabled(self):
        return self.setting.point_type is not None

    def get_cms_data(self):
        return {"organization_id": self.id, "organization_source": "oauth"}


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
    zip = Column(Unicode(32))
    country = Column(Unicode(64))
    prefecture = Column(Unicode(64), nullable=False, default=u'')
    city = Column(Unicode(255), nullable=False, default=u'')
    address_1 = Column(Unicode(255), nullable=False, default=u'')
    address_2 = Column(Unicode(255))
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

def no_filter(value):
    return value


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
    display_order = Column(Identifier)

    def detect_preview_type(self):
        for dm in self.delivery_methods:
            if unicode(dm.delivery_plugin_id) == unicode(plugins.SEJ_DELIVERY_PLUGIN_ID):
                return "sej"
        return "default"


class Ticket(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Ticket.event_idがNULLのものはマスターデータ。これを雛形として実際にeventとひもづけるTicketオブジェクトを作成する。
    """
    __tablename__ = "Ticket"

    FLAG_ALWAYS_REISSUEABLE = 1
    FLAG_PRINCIPAL = 2

    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=True)
    organization = relationship('Organization', uselist=False, backref=backref('ticket_templates'))
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='tickets')
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id', ondelete='CASCADE'), nullable=False)
    ticket_format = relationship('TicketFormat', uselist=False, backref='tickets')
    name = Column(Unicode(255), nullable=False, default=u'')
    flags = Column(Integer, nullable=False, default=FLAG_PRINCIPAL)
    original_ticket_id = Column(Identifier, ForeignKey('Ticket.id', ondelete='SET NULL'), nullable=True)
    derived_tickets = relationship('Ticket', backref=backref('original_ticket', remote_side=[id],),
                                   foreign_keys=[original_ticket_id], primaryjoin="Ticket.id==Ticket.original_ticket_id")
    base_template_id = Column(Identifier, ForeignKey('Ticket.id', ondelete='SET NULL'), nullable=True)
    base_template = relationship('Ticket', uselist=False, remote_side=[id],
                                 foreign_keys=[base_template_id], primaryjoin="Ticket.id==Ticket.base_template_id")
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))
    filename = Column(Unicode(255), nullable=False, default=u"uploaded.svg")
    cover_print = Column(Boolean, nullable=False, default=True)

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

    @property
    def fill_mapping(self):
        return self.data.get("fill_mapping", {})


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
        flags = self.flags or 0
        return (flags & self.FLAG_ALWAYS_REISSUEABLE) != 0

    @always_reissueable.expression
    def principal(self):
        return self.flags.op('&')(self.FLAG_ALWAYS_REISSUEABLE) != 0

    @always_reissueable.setter
    def set_reissueable(self, value):
        flags = self.flags or 0
        if value:
            self.flags = flags | self.FLAG_ALWAYS_REISSUEABLE
        else:
            self.flags = flags & ~self.FLAG_ALWAYS_REISSUEABLE

    @hybrid_property
    def principal(self):
        flags = self.flags or 0
        return (flags & self.FLAG_PRINCIPAL) != 0

    @principal.expression
    def principal(self):
        return self.flags.op('&')(self.FLAG_PRINCIPAL) != 0

    @principal.setter
    def set_principal(self, value):
        flags = self.flags or 0
        if value:
            self.flags = flags | self.FLAG_PRINCIPAL
        else:
            self.flags = flags & ~self.FLAG_PRINCIPAL

    def accept_core_model_traverser(self, traverser):
        traverser.visit_ticket(self)


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
    ordered_product_item = declared_attr(lambda self: relationship('OrderedProductItem'))
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
        return entry

    @classmethod
    def query(cls, operator, ticket_format_id, order_id=None, queue_ids=None, include_masked=False, include_unmasked=True):
        from altair.app.ticketing.orders.models import OrderedProduct, OrderedProductItem
        q = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(processed_at=None, operator=operator) \
            .join(TicketPrintQueueEntry.ticket) \
            .options(joinedload(TicketPrintQueueEntry.seat))
        if not include_masked:
            q = q.filter(TicketPrintQueueEntry.masked_at == None)
        if not include_unmasked:
            q = q.filter(TicketPrintQueueEntry.masked_at != None)
        if ticket_format_id is not None:
            q = q.filter(Ticket.ticket_format_id == ticket_format_id)
        if order_id is not None:
            q = q.join(OrderedProductItem) \
                .join(OrderedProduct) \
                .filter(OrderedProduct.order_id==order_id)
        if queue_ids:
            q = q.filter(cls.id.in_(queue_ids))
        q = q.order_by(*cls.printing_order_condition())
        return q

    @classmethod
    def peek(cls, operator, ticket_format_id, order_id=None, queue_ids=None):
        q = cls.query(operator, ticket_format_id, order_id, queue_ids)
        return q.all()

    @classmethod
    def printing_order_condition(cls):
        return (TicketPrintQueueEntry.created_at, TicketPrintQueueEntry.id)


    @classmethod
    def dequeue(self, ids, now=None):
        from altair.app.ticketing.orders.models import OrderedProduct, OrderedProductItem
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
                _entries = relevant_orders.get(order)
                if _entries is None:
                    _entries = relevant_orders[order] = []
                else:
                    if len(_entries) > 1:
                        logger.info("More than one entry exist for the same order (%d)" % order.id)
                _entries.append(entry)
            else:
                logger.info("TicketPrintQueueEntry #%d is not associated with the order" % entry.id)

        for order, _entries in relevant_orders.items():
            for entry in _entries:
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
    def get_from_order(cls, order, ticket_format_id=None):
        q = TicketCover.query.filter_by(organization_id=order.organization_id)
        if ticket_format_id is not None:
            q = q.join(TicketCover.ticket).filter(Ticket.ticket_format_id == ticket_format_id)
        return q.first() #todo: DeliveryMethod?

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
        relevant_tickets = ApplicableTicketsProducer(self).include_delivery_id_ticket_iter([delivery_plugin_id])
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

    def accept_core_model_traverser(self, traverser):
        traverser.begin_ticket_bundle(self)
        for attribute in self.attributes_.values():
            attribute.accept_core_model_traverser(traverser)
        traverser.end_ticket_bundle(self)

class TicketPrintHistory(Base, BaseModel, WithTimestamp):
    __tablename__ = "TicketPrintHistory"
    __clone_excluded__ = ['operator', 'seat', 'ticket']

    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id'), nullable=True)
    operator = relationship('Operator', uselist=False)
    ordered_product_item_id = Column(Identifier, ForeignKey('OrderedProductItem.id'), nullable=True)
    ordered_product_item = declared_attr(lambda self: relationship('OrderedProductItem', backref='print_histories'))
    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=True)
    seat = relationship('Seat', backref='print_histories')
    item_token_id = Column(Identifier, ForeignKey('OrderedProductItemToken.id'), nullable=True)
    item_token = declared_attr(lambda self:relationship('OrderedProductItemToken'))
    order_id = Column(Identifier, ForeignKey('Order.id'), nullable=True)
    # order = declared_attr(lambda self: relationship('Order'))
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
    display_order = Column(Identifier)

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
    PurcacheSejRemindMail = 3
    LotsAcceptedMail = 11
    LotsElectedMail = 12
    LotsRejectedMail = 13
    PointGrantingFailureMail = 21

_mail_type_labels = {
    MailTypeEnum.PurchaseCompleteMail.v: u"購入完了メール",
    MailTypeEnum.PurchaseCancelMail.v: u"購入キャンセルメール",
    MailTypeEnum.PurcacheSejRemindMail.v: u"リマインドメール",
    MailTypeEnum.LotsAcceptedMail.v: u"抽選申し込み完了メール",
    MailTypeEnum.LotsElectedMail.v: u"抽選当選通知メール",
    MailTypeEnum.LotsRejectedMail.v: u"抽選落選通知メール",
    MailTypeEnum.PointGrantingFailureMail.v: u"ポイント付与失敗通知メール",
    }

MailTypeChoices = [(str(e) , _mail_type_labels[e.v]) for e in sorted(iter(MailTypeEnum), key=lambda e: e.v)]
MailTypeEnum.dict = dict(MailTypeChoices)
MailTypeEnum.as_string = classmethod(lambda cls, e: cls.dict.get(str(e), ""))

class Host(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Host'
    __table_args__ = (
        UniqueConstraint('host_name', 'path'),
        )
    query = DBSession.query_property()

    id = AnnotatedColumn(Identifier, primary_key=True, _a_label=u'ID')
    host_name = AnnotatedColumn(Unicode(255), _a_label=u'ホスト名')
    organization_id = AnnotatedColumn(Identifier, ForeignKey('Organization.id'), _a_label='organization')
    organization = relationship('Organization', backref="hosts")
    base_url = AnnotatedColumn(Unicode(255), _a_label=u'ベースURL (PC・スマートフォン)')
    mobile_base_url = AnnotatedColumn(Unicode(255), _a_label=u'ベースURL (フィーチャーフォン)')
    path = AnnotatedColumn(Unicode(255), _a_label=u'パス')

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

class RefundStatusEnum(StandardEnum):
    Waiting = 0
    Refunding = 1
    Refunded = 2

class Refund_Performance(Base):
    __tablename__ = 'Refund_Performance'
    refund_id = Column(Unicode(48), ForeignKey('Refund.id', ondelete='CASCADE'), primary_key=True)
    performance_id = Column(Identifier, ForeignKey('Performance.id', ondelete='CASCADE'), primary_key=True)

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
    need_stub = Column(Integer, nullable=True, default=None)
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization')
    performances = relationship('Performance', secondary=Refund_Performance.__table__)
    order_count = Column(Integer, nullable=True)
    status = Column(Integer, nullable=False, default=0, server_default='0')

    def editable(self):
        return self.status == RefundStatusEnum.Waiting.v

    def breakdowns(self):
        from altair.app.ticketing.orders.models import Order
        from sqlalchemy import distinct

        stmt = Order.total_amount
        if not self.include_item:
            stmt = stmt - (Order.total_amount - Order.system_fee - Order.transaction_fee - Order.delivery_fee - Order.special_fee)
        if not self.include_system_fee:
            stmt = stmt - Order.system_fee
        if not self.include_transaction_fee:
            stmt = stmt - Order.transaction_fee
        if not self.include_delivery_fee:
            stmt = stmt - Order.delivery_fee
        if not self.include_special_fee:
            stmt = stmt - Order.special_fee

        refund_payment_method = aliased(PaymentMethod, name='refund_payment_method')
        query = DBSession.query(Order).join(
                Order.performance,
                Order.payment_delivery_pair,
                PaymentDeliveryMethodPair.payment_method,
                PaymentDeliveryMethodPair.delivery_method,
                Order.refund,
            ).filter(
                Refund.id==self.id,
                Refund.payment_method_id==refund_payment_method.id,
            ).with_entities(
                Performance.name.label('performance_name'),
                PaymentMethod.name.label('payment_method_name'),
                DeliveryMethod.name.label('delivery_method_name'),
                Order.issued.label('issued'),
                refund_payment_method.name.label('refund_payment_method_name'),
                func.count(distinct(Order.id)).label('order_count'),
                func.sum(stmt).label('amount'),
            ).group_by(
                Performance.id,
                PaymentMethod.id,
                DeliveryMethod.id,
                Order.issued,
                Refund.payment_method_id,
            )
        return query.all()

    def delete(self):
        if not self.editable():
            raise InvalidRefundStateError(u'払戻中または払戻済の為、削除できません')
        for order in self.orders:
            order.refund_id = None
            order.save()
        super(Refund, self).delete()


@implementer(ISettingContainer, IOrderQueryable)
class SalesSegment(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'SalesSegment'
    query = DBSession.query_property()

    id = Column(Identifier, primary_key=True)
    start_at = AnnotatedColumn(DateTime, _a_label=_(u'販売開始'))
    end_at = AnnotatedColumn(DateTime, _a_label=_(u'販売終了'))
    max_quantity = AnnotatedColumn('upper_limit', Integer, _a_label=_(u'購入上限枚数'))
    order_limit = association_proxy('setting', 'order_limit', creator=lambda order_limit: SalesSegmentSetting(order_limit=order_limit))
    max_product_quatity = AnnotatedColumn('product_limit', Integer, _a_label=_(u'商品購入上限数'))

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
    auth3d_notice = AnnotatedColumn(UnicodeText, _a_label=_(u'クレジットカード 3D認証フォーム 注記事項'))

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
    use_default_order_limit = association_proxy('setting', 'use_default_order_limit', creator=lambda use_default_order_limit: SalesSegmentSetting(use_default_order_limit=use_default_order_limit))
    use_default_max_quantity = Column('use_default_upper_limit', Boolean)
    use_default_max_product_quatity = Column('use_default_product_limit', Boolean)
    use_default_account_id = Column(Boolean)
    use_default_margin_ratio = Column(Boolean)
    use_default_refund_ratio = Column(Boolean)
    use_default_printing_fee = Column(Boolean)
    use_default_registration_fee = Column(Boolean)
    use_default_auth3d_notice = Column(Boolean)

    setting = relationship('SalesSegmentSetting', uselist=False, backref='sales_segment', cascade='all', lazy='joined')

    def has_stock_type(self, stock_type):
        return stock_type in self.seat_stock_types

    def has_stock(self, stock):
        return stock in self.stocks

    def available_payment_delivery_method_pairs(self, now):
        return [pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.is_available_for(self, now)]


    def query_orders_by_user(self, user, filter_canceled=False, query=None):
        """ 該当ユーザーがこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query.filter(
            Order.user_id==user.id
        ).filter(
            Order.sales_segment_id==self.id
        )
        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs

    def query_orders_by_mailaddresses(self, mailaddresses, filter_canceled=False, query=None):
        """ 該当メールアドレスによるこの販売区分での注文内容を問い合わせ """
        from altair.app.ticketing.orders.models import Order
        if query is None:
            query = DBSession.query(Order)
        qs = query.filter(
            Order.shipping_address_id==ShippingAddress.id
        ).filter(
            or_(ShippingAddress.email_1.in_(mailaddresses),
                ShippingAddress.email_2.in_(mailaddresses))
        ).filter(
            Order.sales_segment_id==self.id
        )

        if filter_canceled:
            qs = qs.filter(Order.canceled_at==None)
        return qs

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
        products = DBSession.query(Product, include_deleted=True).options(undefer(Product.deleted_at)).filter_by(sales_segment_id=self.id).all()
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
        if template.setting is not None:
            sales_segment.setting = SalesSegmentSetting.create_from_template(template.setting)
        if 'performance_id' in kwargs:
            sales_segment.performance_id = kwargs['performance_id']
            p = Performance.query.get(kwargs['performance_id'])
            sales_segment.event_id = p.event_id
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

    def is_deletable(self):
        """販売区分は商品か抽選が紐付いている場合は削除できない

        削除ができる状態の場合はTrueが返ります。
        """
        return not (bool(self.products) or bool(self.lots))

    def delete(self, force=False):
        # delete Product
        for product in self.products:
            product.delete()
        super(type(self), self).delete()

    def get_amount(self, pdmp, product_price_quantity_triplets):
        return pdmp.per_order_fee + self.get_products_amount(pdmp, product_price_quantity_triplets)

    def get_transaction_fee(self, pdmp, product_quantities):
        return pdmp.transaction_fee_per_order + sum([
            (pdmp.transaction_fee_per_product + \
             pdmp.transaction_fee_per_ticket * product.num_principal_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_delivery_fee(self, pdmp, product_quantities):
        return pdmp.delivery_fee_per_order + sum([
            (pdmp.delivery_fee_per_product + \
             pdmp.delivery_fee_per_principal_ticket * product.num_principal_tickets(pdmp) + \
             pdmp.delivery_fee_per_subticket * product.num_subtickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_system_fee(self, pdmp, product_quantities):
        return pdmp.system_fee_per_order + sum([
            (pdmp.system_fee_per_product + \
             pdmp.system_fee_per_ticket * product.num_principal_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_special_fee(self, pdmp, product_quantities):
        return pdmp.special_fee_per_order + sum([
            (pdmp.special_fee_per_product + \
             pdmp.special_fee_per_ticket * product.num_principal_tickets(pdmp)) * quantity
            for product, quantity in product_quantities])

    def get_products_amount(self, pdmp, product_price_quantity_triplets):
        return sum([
            (price + \
             pdmp.per_product_fee + \
             (pdmp.per_ticket_fee_excluding_delivery_fee + pdmp.delivery_fee_per_principal_ticket) * product.num_principal_tickets(pdmp) + \
             pdmp.delivery_fee_per_subticket * product.num_subtickets(pdmp)) * quantity
            for product, price, quantity in product_price_quantity_triplets])

    def get_products_amount_without_fee(self, pdmp, product_price_quantity_triplets):
        return sum([
            price * quantity
            for product, price, quantity in product_price_quantity_triplets])

    def applicable(self, user=None, now=None, type='available'):
        return build_sales_segment_query(sales_segment_id=self.id, user=user, now=now, type=type).count() > 0

    def accept_core_model_traverser(self, traverser):
        traverser.begin_sales_segment(self)
        if self.setting is not None:
            traverser.visit_sales_segment_setting(self.setting)
        for product in self.products:
            product.accept_core_model_traverser(traverser)
        traverser.end_sales_segment(self)

class SalesReportTypeEnum(StandardEnum):
    Default = 1
    Simple = 2

@implementer(ISetting)
class OrganizationSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "OrganizationSetting"
    id = Column(Identifier, primary_key=True)
    DEFAULT_NAME = u"default"
    name = AnnotatedColumn(Unicode(255), default=DEFAULT_NAME, _a_label=u'名称')
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='settings')

    auth_type = AnnotatedColumn(Unicode(255), _a_label=u"認証方式")
    performance_selector = association_proxy('cart_setting', 'performance_selector')
    margin_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=u"販売手数料率")
    refund_ratio = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=u"払戻手数料率")
    printing_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=u"印刷代金(円/枚)")
    registration_fee = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, default=0, server_default='0', _a_label=u"登録手数料")

    multicheckout_shop_name = AnnotatedColumn(Unicode(255), unique=True, _a_label=u"マルチ決済店舗名称")
    multicheckout_shop_id = AnnotatedColumn(Unicode(255), _a_label=u"マルチ決済店舗ID")
    multicheckout_auth_id = AnnotatedColumn(Unicode(255), _a_label=u"マルチ決済APIユーザID")
    multicheckout_auth_password = AnnotatedColumn(Unicode(255), _a_label=u"マルチ決済APIパスワード")

    cart_item_name = AnnotatedColumn(Unicode(255), _a_label=u"マルチ決済決済項目名")

    contact_pc_url = AnnotatedColumn(Unicode(255), _a_label=u"お問い合わせ先URL (PC)")
    contact_mobile_url = AnnotatedColumn(Unicode(255), _a_label=u"お問い合わせ先URL (mobile)")

    point_type = AnnotatedColumn(Integer, nullable=True, _a_label=u"ポイントサービス種別")
    point_fixed = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=True, _a_label=u"付与ポイントデフォルト値 (固定)")
    point_rate = AnnotatedColumn(Float, nullable=True, _a_label=u"付与ポイントデフォルト値 (率)")

    bcc_recipient = AnnotatedColumn(Unicode(255), nullable=True, _a_label=u"BCC受信者")
    default_mail_sender = AnnotatedColumn(Unicode(255), _a_label=u"デフォルトの送信元メールアドレス")
    entrust_separate_seats = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"バラ席のおまかせが有効", _a_label=u"おまかせ座席選択でバラ席を許可する")
    notify_point_granting_failure = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"ポイント付与失敗時のメール通知on/off", _a_label=u"ポイント付与失敗時のメール通知を有効にする")
    notify_remind_mail = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"コンビニ入金期限前リマインドメールのメール通知on/off", _a_label=u"コンビニ入金期限前リマインドメールのメール通知を有効にする")
    sales_report_type = AnnotatedColumn(Integer, nullable=False, default=1, server_default='1', _a_label=u"売上レポートタイプ")

    # augus
    augus_use = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"オーガス連携", _a_label=u"オーガス連携")

    enable_smartphone_cart = AnnotatedColumn(Boolean, nullable=False, default=False, _a_label=u'スマートフォン用のカートを有効にする')
    enable_mypage = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"マイページの使用", _a_label=u"マイページの使用")
    cart_setting_id = AnnotatedColumn(Identifier, ForeignKey('CartSetting.id'), default=None, _a_label=_(u'カートの種類'), _a_visible_column=True)
    cart_setting = relationship('CartSetting')
    asid = AnnotatedColumn(Unicode(255), doc=u"asid", _a_label=u"asid")
    asid_mobile = AnnotatedColumn(Unicode(255), doc=u"asid_mobile", _a_label=u"asid_mobile")
    asid_smartphone = AnnotatedColumn(Unicode(255), doc=u"asid_smartphone", _a_label=u"asid_smartphone")
    lot_asid = AnnotatedColumn(Unicode(255), doc=u"lot_asid", _a_label=u"lot_asid")
    sitecatalyst_use = AnnotatedColumn(Boolean, nullable=False, default=False, doc=u"SiteCatalystの使用", _a_label=u"SiteCatalystの使用")

    def _render_cart_setting_id(self):
        return link_to_cart_setting(self.cart_setting)

    @property
    def container(self):
        return self.organization

@implementer(ISetting, IAllAppliedSetting, IChainedSetting)
class EventSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "EventSetting"
    id = Column(Identifier, primary_key=True)
    event_id = Column(Identifier, ForeignKey('Event.id'))

    performance_selector = association_proxy('cart_setting', 'performance_selector')
    performance_selector_label1_override = association_proxy('cart_setting', 'performance_selector_label1_override')
    performance_selector_label2_override = association_proxy('cart_setting', 'performance_selector_label2_override')
    order_limit = AnnotatedColumn(Integer, default=None, _a_label=_(u'購入回数制限'), _a_visible_column=True)
    max_quantity_per_user = AnnotatedColumn(Integer, default=None, _a_label=(u'購入上限枚数 (購入者毎)'), _a_visible_column=True)
    middle_stock_threshold = AnnotatedColumn(Integer, default=None, _a_label=_(u'カート在庫閾値 (残席数)'), _a_visible_column=True)
    middle_stock_threshold_percent = AnnotatedColumn(Integer, default=None, _a_label=_(u'カート在庫閾値 (%)'), _a_visible_column=True)
    cart_setting_id = AnnotatedColumn(Identifier, ForeignKey('CartSetting.id'), default=None, _a_label=_(u'カートの種類'), _a_visible_column=True)
    cart_setting = relationship('CartSetting')

    @property
    def super(self):
        return None

    @property
    def container(self):
        return self.event

    @classmethod
    def create_from_template(cls, template, event_id=None, **kwargs):
        setting = cls.clone(template)
        setting.event_id = event_id
        setting.save() # XXX
        return setting


@implementer(IAllAppliedSetting)
class SalesSegmentGroupSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SalesSegmentGroupSetting"
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    sales_segment_group_id = Column(Identifier, ForeignKey('SalesSegmentGroup.id'))
    order_limit = AnnotatedColumn(Integer, default=None, _a_label=_(u'購入回数制限'))
    max_quantity_per_user = AnnotatedColumn(Integer, default=None, _a_label=(u'購入上限枚数 (購入者毎)'), _a_visible_column=True)
    disp_orderreview = AnnotatedColumn(Boolean, default=True,
                                  _a_label=_(u'マイページへの購入履歴表示／非表示'))
    disp_agreement = AnnotatedColumn(Boolean, default=True, _a_label=_(u'規約の表示／非表示'))
    agreement_body = AnnotatedColumn(UnicodeText, _a_label=_(u"規約内容"), default=u"")
    display_seat_no = AnnotatedColumn(Boolean, default=True, server_default='1', _a_label=_(u'座席番号の表示可否'))
    sales_counter_selectable = AnnotatedColumn(Boolean, default=True, server_default='1', _a_label=_(u'窓口業務で閲覧可能'))
    extra_form_fields = deferred(AnnotatedColumn(MutationDict.as_mutable(JSONEncodedDict(16384)), _a_label=_(u'追加フィールド')))

    @classmethod
    def create_from_template(cls, template, **kwargs):
        setting = cls.clone(template)
        setting.save() # XXX
        return setting


@implementer(ISetting, IAllAppliedSetting, IChainedSetting)
class SalesSegmentSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SalesSegmentSetting"
    id = Column(Identifier, primary_key=True, autoincrement=True, nullable=False)
    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'))
    order_limit = AnnotatedColumn(Integer, default=None, _a_label=_(u'購入回数制限'))
    max_quantity_per_user = AnnotatedColumn(Integer, default=None, _a_label=(u'購入上限枚数 (購入者毎)'), _a_visible_column=True)
    disp_orderreview = AnnotatedColumn(Boolean, default=True,
                                  _a_label=_(u'マイページへの購入履歴表示／非表示'))
    disp_agreement = AnnotatedColumn(Boolean, default=True, _a_label=_(u'規約の表示／非表示'))
    agreement_body = AnnotatedColumn(UnicodeText, _a_label=_(u"規約内容"), default=u"")
    display_seat_no = AnnotatedColumn(Boolean, default=True, server_default='1', _a_label=_(u'座席番号の表示可否'))
    sales_counter_selectable = AnnotatedColumn(Boolean, default=True, server_default='1', _a_label=_(u'窓口業務で閲覧可能'))
    extra_form_fields = deferred(AnnotatedColumn(MutationDict.as_mutable(JSONEncodedDict(16384)), _a_label=_(u'追加フィールド')))

    use_default_order_limit = Column(Boolean)
    use_default_max_quantity_per_user = Column(Boolean)
    use_default_disp_orderreview = Column(Boolean)
    use_default_display_seat_no = Column(Boolean)
    use_default_disp_agreement = Column(Boolean)
    use_default_agreement_body = Column(Boolean)
    use_default_sales_counter_selectable = Column(Boolean)
    use_default_extra_form_fields = Column(Boolean)

    @property
    def super(self):
        performance = self.sales_segment.performance
        if performance is not None and performance.setting is not None:
            return performance.setting
        else:
            event = self.sales_segment.event
            if event is not None and event.setting is not None:
                return event.setting
        return None

    @property
    def container(self):
        return self.sales_segment

    @classmethod
    def create_from_template(cls, template, **kwargs):
        setting = cls.clone(template)
        setting.save() # XXX
        return setting

@implementer(ISetting, IAllAppliedSetting, IChainedSetting)
class PerformanceSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "PerformanceSetting"
    id = Column(Identifier, primary_key=True)
    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    order_limit = AnnotatedColumn(Integer, default=None, _a_label=_(u'購入回数制限'), _a_visible_column=True)
    entry_limit = AnnotatedColumn(Integer, default=None, _a_label=_(u'申込回数制限'), _a_visible_column=True)
    max_quantity_per_user = AnnotatedColumn(Integer, default=None, _a_label=(u'購入上限枚数 (購入者毎)'), _a_visible_column=True)

    @property
    def super(self):
        event = self.performance.event
        if event is not None and event.setting is not None:
            return event.setting
        return None

    @property
    def container(self):
        return self.performance

    @classmethod
    def create_from_template(cls, template, **kwargs):
        setting = cls.clone(template)
        setting.save() # XXX
        return setting


@implementer(ISejTenant)
class SejTenant(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejTenant'
    id                      = Column(Identifier, primary_key=True)
    shop_name               = Column(String(12))
    shop_id                 = Column(String(12))
    contact_01              = Column(String(128))
    contact_02              = Column(String(255))
    api_key                 = Column(String(255), nullable=True)
    inticket_api_url        = Column(String(255), nullable=True)
    nwts_endpoint_url       = Column(String(255), nullable=True)
    nwts_terminal_id        = Column(String(255), nullable=True)
    nwts_password           = Column(String(255), nullable=True)

    organization_id         = Column(Identifier)


class CooperationTypeEnum(StandardEnum):
    augus = (1, u'オーガス')
    #gettie = (2, u'Gettie')


class AugusAccount(Base, BaseModel):
    __tablename__ = 'AugusAccount'

    id = Column(Identifier, primary_key=True)
    code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'企業コード')) # PK
    name = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'名称'))
    host = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'FTPサーバのURL'))
    username = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'ユーザー名'))
    password = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'パスワード'))
    send_dir = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'送り側ディレクトリ'))
    recv_dir = AnnotatedColumn(Unicode, nullable=False,  _a_label=(u'受け側ディレクトリ'))

    account_id = Column(Identifier, ForeignKey('Account.id'), nullable=False, unique=True)#, _a_label=(u'アカウント')) # PK
    account = relationship('Account', uselist=False, backref=backref('augus_account', uselist=False))
    organization = association_proxy('account', 'organization')


class AugusVenue(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusVenue'

    id = Column(Identifier, primary_key=True)
    code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'会場コード'))
    name = AnnotatedColumn(Unicode(32), nullable=False,  _a_label=(u'会場名'))
    version = AnnotatedColumn(Integer, nullable=False,
                              _a_label=(u'会場バージョン'))
    venue_id = Column(Identifier, ForeignKey('Venue.id'), nullable=False)
    venue = relationship('Venue')
    reserved_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'会場連携通知予約日時'))
    notified_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'会場連携通知日時'))

    augus_account_id = Column(Identifier, ForeignKey('AugusAccount.id'), nullable=True)
    augus_account = relationship('AugusAccount', backref='augus_venues')

class AugusSeat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusSeat'
    __table_args__= (
        UniqueConstraint('area_code', 'info_code', 'floor',
                         'column', 'num', 'augus_venue_id',
                         name="uix_AugusSeat"),
    )
    id = Column(Identifier, primary_key=True)
    area_name = AnnotatedColumn(Unicode(32), nullable=False,
                                _a_label=(u'エリア名'), default=u'')
    info_name = AnnotatedColumn(Unicode(32), nullable=False,
                                _a_label=(u'付加情報'), default=u'')
    doorway_name = AnnotatedColumn(Unicode(32), nullable=False,
                                   _a_label=(u'出入口'), default=u'')
    priority = AnnotatedColumn(Integer, nullable=False, default=u'', _a_label=(u'優先度'))
    floor = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u"階"))
    column = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u"列"))
    num = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u"番"))
    block = AnnotatedColumn(Integer, nullable=False, _a_label=(u'ブロック'))
    coordy = AnnotatedColumn(Integer, nullable=False, _a_label=(u'Y座標'))
    coordx = AnnotatedColumn(Integer, nullable=False, _a_label=(u'X座標'))
    coordy_whole = AnnotatedColumn(Integer, nullable=False, _a_label=(u'Y座標2'))
    coordx_whole = AnnotatedColumn(Integer, nullable=False, _a_label=(u'X座標2'))
    area_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'エリアコード'))
    info_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'付加情報コード'))
    doorway_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'出入口コード'))
    version = AnnotatedColumn(Integer, nullable=False, _a_label=(u'会場バージョン'))

    augus_venue_id = Column(Identifier, ForeignKey('AugusVenue.id', ondelete='CASCADE'), nullable=False)
    seat_id = Column(Identifier, ForeignKey('Seat.id'))
    augus_venue = relationship('AugusVenue', backref='augus_seats')
    seat = relationship('Seat')


    def __unicode__(self):
        return u'{{}}'.format(u', '.join([self.augus_venue.name,
                                          str(self.augus_venue.version),
                                          self.area_name,
                                          self.info_name,
                                          self.floor,
                                          self.column,
                                          self.num
                                      ]))

class AugusPerformance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusPerformance'
    id = Column(Identifier, primary_key=True)
    augus_event_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス事業コード'))
    augus_performance_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス公演コード'))
    augus_venue_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス会場コード'))
    augus_venue_name = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'オーガス会場名'))
    augus_event_name = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'オーガス事業名'))
    augus_performance_name = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'オーガス公演名'))
    open_on = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'開場日時'))
    start_on = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'公演日時'))
    augus_venue_version = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス会場バージョン'))

    is_report_target = Column(Boolean, nullable=True, default=False)
    stoped_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'連携終了日時'))

    performance_id = Column(Identifier,
                            ForeignKey("Performance.id"),
                            nullable=True, unique=True)
    performance = relationship('Performance', backref='augus_performances')
    augus_stock_infos = relationship('AugusStockInfo')

    augus_account_id = Column(Identifier, ForeignKey('AugusAccount.id'), nullable=True)
    augus_account = relationship('AugusAccount', backref='augus_performances')

    @property
    def code(self):
        return self.augus_performance_code

    def get_augus_venue(self):
        try:
            return AugusVenue.query.filter(AugusVenue.code==self.augus_venue_code)\
                                   .filter(AugusVenue.version==self.augus_venue_version)\
                                   .one()
        except NoResultFound as err:
            return None

class AugusTicket(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusTicket'
    id = Column(Identifier, primary_key=True)
    augus_venue_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス会場コード'))
    augus_seat_type_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス席種コード'))
    augus_seat_type_name = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'オーガス席種名'))
    unit_value_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'オーガス単価コード'))
    unit_value_name = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'単価名称'))
    augus_seat_type_classif = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'席区分'))
    value = AnnotatedColumn(Integer, nullable=False, _a_label=(u'売値'))

    stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=True)
    stock_type = relationship('StockType')

    augus_performance_id = Column(Identifier, ForeignKey('AugusPerformance.id'), nullable=True)
    augus_performance = relationship('AugusPerformance', backref='augus_tickets')

    augus_event_code = association_proxy('augus_performance', 'augus_event_code')
    augus_performance_code = association_proxy('augus_performance', 'augus_performance_code')

    augus_account_id = Column(Identifier, ForeignKey('AugusAccount.id'), nullable=True)
    augus_account = relationship('AugusAccount', backref='augus_tickets')


    def link_stock_type(self, stock_type):
        if not self.augus_performance.performance in stock_type.event.performances:
            raise ValueError('illegal performance')
        self.stock_type_id = stock_type.id

    def delete_link(self):
        self.stock_type_id = None

class AugusStockDetail(Base, BaseModel):
    __tablename__ = 'AugusStockDetail'
    id = Column(Identifier, primary_key=True)
    augus_distribution_code = AnnotatedColumn(Integer, nullable=False)
    augus_seat_type_code = AnnotatedColumn(Integer, nullable=False)
    augus_unit_value_code = AnnotatedColumn(Integer, nullable=False)
    start_on = AnnotatedColumn(DateTime, nullable=False)
    seat_type_classif = AnnotatedColumn(Integer, nullable=False)
    augus_unit_value_code = AnnotatedColumn(Integer, nullable=False)
    quantity = AnnotatedColumn(Integer, nullable=False, default=0)

    augus_stock_info_id = Column(Identifier, ForeignKey('AugusStockInfo.id'), nullable=True)
    augus_stock_info = relationship('AugusStockInfo', backref='augus_stock_details')
    augus_putback_id = Column(Identifier, ForeignKey('AugusPutback.id'), nullable=True)
    augus_putback = relationship('AugusPutback', backref='augus_stock_details')
    augus_ticket_id = Column(Identifier, ForeignKey('AugusTicket.id'), nullable=True)
    augus_ticket = relationship('AugusTicket', backref='augus_stock_details')
    distributed_at = Column(DateTime, nullable=True)


class AugusStockInfo(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusStockInfo'
    id = Column(Identifier, primary_key=True)
    augus_distribution_code = AnnotatedColumn(Integer, _a_label=(u'オーガス配券コード'))
    seat_type_classif = AnnotatedColumn(Unicode(32), _a_label=(u'席区分'))
    distributed_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'配券日時'))
    quantity = AnnotatedColumn(Integer, _a_label=(u'席数'), nullable=False)

    augus_performance_id = Column(Identifier, ForeignKey('AugusPerformance.id'), nullable=False)
    augus_performance = relationship('AugusPerformance')

    augus_ticket_id = Column(Identifier, ForeignKey('AugusTicket.id'), nullable=False)
    augus_ticket = relationship('AugusTicket')

    augus_seat_id = Column(Identifier, ForeignKey('AugusSeat.id'), nullable=False)
    augus_seat = relationship('AugusSeat')

    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=False)
    seat = relationship('Seat')

    putbacked_at = Column(DateTime, nullable=True, default=None)

    augus_account_id = Column(Identifier, ForeignKey('AugusAccount.id'), nullable=True)
    augus_account = relationship('AugusAccount', uselist=False, backref='augus_stock_infos')


    def get_seat(self):
        performance = self.augus_performance
        if not performance:
            return None
        venue = performance.venue
        l0_id = self.augus_seat.seat.l0_id
        for seat in venue.seats:
            if seat.l0_id == l0_id:
                return seat
        return None

    def get_augus_ticket(self):
        seat = self.get_seat()

        if seat:
            stock_type = seat.stock.stock_type if seat.stock else None
            if stock_type:
                return AugusTicket.get(stock_type_id=stock_type.id)
        return None

    @property
    def putback_status(self):
        if self.seat.status in [SeatStatusEnum.NotOnSale.v, SeatStatusEnum.Vacant.v, SeatStatusEnum.Canceled.v]:
            return AugusPutbackStatus.CANDO
        else:
            return AugusPutbackStatus.CANNOT


class AugusPutbackStatus:
    CANDO = 0
    CANNOT = 1

class AugusPutbackType:
    ROUTE = u'R' # 途中
    FINAL = u'F' # 最終

class AugusPutback(Base, BaseModel): #, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AugusPutback'
    id = Column(Identifier, primary_key=True)
    augus_putback_code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'返券コード'))
    reserved_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'返券予約日時'))
    notified_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'返券通知日時'))
    finished_at = AnnotatedColumn(TIMESTAMP(), nullable=True, _a_label=(u'返券完了日時'))
    augus_putback_type = AnnotatedColumn(Unicode(32), _a_label=(u'返券区分'), default=AugusPutbackType.ROUTE)
    augus_performance_id = Column(Identifier, ForeignKey('AugusPerformance.id'), nullable=False)
    augus_performance = relationship('AugusPerformance')

    augus_account_id = Column(Identifier, ForeignKey('AugusAccount.id'), nullable=True)
    augus_account = relationship('AugusAccount', backref='augus_putbacks')


    def __len__(self):
        return len(self.augus_stock_details)


class AugusSeatStatus(object):
    RESERVE = 0
    SOLD = 1
    OTHER = 99

    @classmethod
    def get_status(cls, seat, order=None):
        if seat.status in (SeatStatusEnum.Keep.v,
                           SeatStatusEnum.Import.v,
                           SeatStatusEnum.InCart.v,
                           SeatStatusEnum.Confirmed.v,
                           SeatStatusEnum.Reserved.v,
                           ):
            return cls.RESERVE
        elif seat.status in (SeatStatusEnum.Ordered.v,
                             SeatStatusEnum.Shipped.v,
                             ):
            if order and order.payment_status == 'paid':
                return cls.SOLD
            else:
                return cls.RESERVE
        else:
            return cls.OTHER


class OrionPerformance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrionPerformance'

    id = Column(Identifier, primary_key=True)
    performance_id = Column(Identifier, ForeignKey('Performance.id'), nullable=False)
    performance = relationship('Performance', backref=backref('orion', uselist=False))

    instruction_general = Column(UnicodeText(8388608))
    instruction_performance = Column(UnicodeText(8388608))
    web = Column(Unicode(255))
    header_url = Column(Unicode(255))
    background_url = Column(Unicode(255))
    icon_url = Column(Unicode(255))

    qr_enabled = Column(Boolean)
    pattern = Column(Unicode(255))

    coupon_2_name = Column(Unicode(255))
    coupon_2_qr_enabled = Column(Boolean)
    coupon_2_pattern = Column(Unicode(255))


class CartMixin(object):
    @property
    def issuing_start_at(self):
        assert self.payment_delivery_pair is not None
        assert self.created_at is not None
        # XXX: created_at はカート生成日時なので、Order 生成時に再計算する必要あり
        return calculate_date_from_order_like(
            self,
            self.payment_delivery_pair.issuing_start_day_calculation_base,
            DateCalculationBias.StartOfDay.v,
            self.payment_delivery_pair.issuing_interval_days,
            self.payment_delivery_pair.issuing_start_at
            )

    @property
    def issuing_end_at(self):
        assert self.payment_delivery_pair is not None
        assert self.created_at is not None
        # XXX: created_at はカート生成日時なので、Order 生成時に再計算する必要あり
        return calculate_date_from_order_like(
            self,
            self.payment_delivery_pair.issuing_end_day_calculation_base,
            DateCalculationBias.EndOfDay.v,
            self.payment_delivery_pair.issuing_end_in_days,
            self.payment_delivery_pair.issuing_end_at
            )

    @property
    def payment_start_at(self):
        assert self.payment_delivery_pair is not None
        assert self.created_at is not None
        # XXX: created_at はカート生成日時なので、Order 生成時に再計算する必要あり
        return calculate_date_from_order_like(
            self,
            self.payment_delivery_pair.payment_start_day_calculation_base,
            DateCalculationBias.StartOfDay.v,
            self.payment_delivery_pair.payment_start_in_days,
            self.payment_delivery_pair.payment_start_at
            )

    @property
    def payment_due_at(self):
        assert self.payment_delivery_pair is not None
        assert self.created_at is not None
        # XXX: created_at はカート生成日時なので、Order 生成時に再計算する必要あり
        return calculate_date_from_order_like(
            self,
            self.payment_delivery_pair.payment_due_day_calculation_base,
            DateCalculationBias.EndOfDay.v,
            self.payment_delivery_pair.payment_period_days,
            self.payment_delivery_pair.payment_due_at
            )

class GettiiVenue(Base, BaseModel):
    __tablename__ = 'GettiiVenue'

    id = Column(Identifier, primary_key=True)
    code = AnnotatedColumn(Integer, nullable=False, _a_label=(u'会場コード'))
    venue_id = Column(Identifier, ForeignKey('Venue.id'), nullable=False)
    venue = relationship('Venue')


class GettiiSeat(Base, BaseModel):
    __tablename__ = 'GettiiSeat'

    id = Column(Identifier, primary_key=True)
    l0_id = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'座席連番'), default=u'')
    coordx = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'座標X'), default=u'')
    coordy = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'座標Y'), default=u'')
    posx = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'位置X'), default=u'')
    posy = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'位置Y'), default=u'')
    angle = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'角度'), default=u'')
    floor = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'階'), default=u'')
    column = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'列'), default=u'')
    num = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'番号'), default=u'')
    block = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'ブロック'), default=u'')
    gate = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'ゲート'), default=u'')
    priority_floor = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'優先順位階'), default=u'')
    priority_area_code = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'優先順位エリアコード'), default=u'')
    priority_block = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'優先順位ブロック'), default=u'')
    priority_seat = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'優先順位座席'), default=u'')
    seat_flag = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'座席フラグ'), default=u'')
    seat_classif = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'座席区分'), default=u'')
    net_block = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'ネットブロック'), default=u'')
    modified_by = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'更新担当者コード'), default=u'')
    modified_at = AnnotatedColumn(Unicode(32), nullable=False, _a_label=(u'更新日'), default=u'')
    # link
    gettii_venue_id = Column(Identifier, ForeignKey('GettiiVenue.id', ondelete='CASCADE'), nullable=False)
    seat_id = Column(Identifier, ForeignKey('Seat.id'), nullable=True)
    gettii_venue = relationship('GettiiVenue', backref='gettii_seats')
    seat = relationship('Seat')
