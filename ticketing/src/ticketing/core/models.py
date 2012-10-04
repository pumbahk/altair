# encoding: utf-8
import logging
import itertools
import operator
import json
from urlparse import urljoin
from datetime import datetime

from sqlalchemy import Table, Column, ForeignKey, func, or_, and_, event
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode, UnicodeText
from sqlalchemy.orm import join, backref, column_property, joinedload, deferred
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import exists
from sqlalchemy.sql.expression import asc, desc, exists, select, table, column
from sqlalchemy.ext.associationproxy import association_proxy

from pyramid.threadlocal import get_current_registry

from .exceptions import *
from ticketing.models import *
from ticketing.users.models import User, UserCredential
from ticketing.utils import sensible_alnum_decode
from ticketing.sej.models import SejOrder
from ticketing.sej.exceptions import SejServerError
from ticketing.sej.payment import request_cancel_order
from ticketing.assets import IAssetResolver
from ticketing.utils import myurljoin

logger = logging.getLogger(__name__)

class Seat_SeatAdjacency(Base):
    __tablename__ = 'Seat_SeatAdjacency'
    seat_id = Column(Identifier, ForeignKey('Seat.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    seat_adjacency_id = Column(Identifier, ForeignKey('SeatAdjacency.id', ondelete='CASCADE'), primary_key=True, nullable=False)

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
    drawing_url = Column(String(255))
    _metadata_url = Column('metadata_url', String(255))

    @property
    def metadata_url(self):
        return self._metadata_url and myurljoin(get_current_registry().settings.get('altair.site_data.base_url', ''), self._metadata_url)

    @property
    def _metadata(self):
        __metadata = getattr(self, '__metadata', None)
        if not __metadata:
            resolver = get_current_registry().queryUtility(IAssetResolver)
            self.__metadata = self.metadata_url and json.load(resolver.resolve(self.metadata_url).stream())
        return self.__metadata

    def get_drawing(self, name):
        page_meta = self._metadata[u'pages'].get(name)
        print self._metadata
        if page_meta is not None:
            resolver = get_current_registry().queryUtility(IAssetResolver)
            return resolver.resolve(myurljoin(self.metadata_url, name))
        else:
            return None

class VenueArea_group_l0_id(Base):
    __tablename__   = "VenueArea_group_l0_id"
    venue_id = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    group_l0_id = Column(String(255), ForeignKey('Seat.group_l0_id', onupdate=None, ondelete='CASCADE'), primary_key=True, nullable=True)
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
    name = Column(String(255))
    sub_name = Column(String(255))

    original_venue_id = Column(Identifier, ForeignKey("Venue.id"), nullable=True)
    derived_venues = relationship("Venue",
                                  backref=backref(
                                    'original_venue', remote_side=[id]))

    site = relationship("Site", uselist=False)
    areas = relationship("VenueArea", backref='venues', secondary=VenueArea_group_l0_id.__table__)
    organization = relationship("Organization", backref='venues')
    seat_index_types = relationship("SeatIndexType", backref='venue')
    attributes = Column(MutationDict.as_mutable(JSONEncodedDict(16384)))

    @staticmethod
    def create_from_template(template, performance_id, original_performance_id=None):
        # 各モデルのコピー元/コピー先のidの対比表
        convert_map = {
            'seat_adjacency':dict(),
            'seat_index_type':dict(),
        }

        # create Venue
        venue = Venue.clone(template)
        venue.original_venue_id = template.id
        venue.performance_id = performance_id
        venue.save()

        # create VenueArea - VenueArea_group_l0_id
        for template_area in template.areas:
            VenueArea.create_from_template(template=template_area, venue_id=venue.id)

        # create SeatAdjacencySet - SeatAdjacency
        for template_adjacency_set in template.adjacency_sets:
            convert_map['seat_adjacency'].update(SeatAdjacencySet.create_from_template(
                template=template_adjacency_set,
                venue_id=venue.id
            ))

        # create SeatIndexType
        for template_seat_index_type in template.seat_index_types:
            convert_map['seat_index_type'].update(
                SeatIndexType.create_from_template(template=template_seat_index_type, venue_id=venue.id)
            )

        # Performanceのコピー時はstockのリレーションもコピーする
        if original_performance_id:
            # stock_idのマッピングテーブル
            convert_map['stock_id'] = dict()
            old_stocks = Stock.filter_by(performance_id=template.performance_id).all()
            for old_stock in old_stocks:
                new_stock_id = Stock.filter_by(performance_id=performance_id)\
                    .filter_by(stock_holder_id=old_stock.stock_holder_id)\
                    .filter_by(stock_type_id=old_stock.stock_type_id)\
                    .with_entities(Stock.id).scalar()
                convert_map['stock_id'][old_stock.id] = new_stock_id

        # create Seat - SeatAttribute, SeatStatus, SeatIndex, Seat_SeatAdjacency
        default_stock = Stock.get_default(performance_id=performance_id)
        for template_seat in template.seats:
            Seat.create_from_template(
                template=template_seat,
                venue_id=venue.id,
                default_stock_id=default_stock.id,
                convert_map=convert_map
            )

        if not original_performance_id:
            # defaultのStockに席数をセット
            stock = Stock.get_default(performance_id=performance_id)
            stock.quantity = len(template.seats)
            stock.save()

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
    def create_from_template(template, venue_id):
        # create VenueArea
        area = VenueArea.clone(template)
        area.venue_id = venue_id
        area.save()

        # create VenueArea_group_l0_id
        for template_group in template.groups:
            group = VenueArea_group_l0_id(
                group_l0_id=template_group.group_l0_id,
                venue_id=venue_id,
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

    @staticmethod
    def create_from_template(template, seat_id):
        # create SeatAttribute
        attribute = SeatAttribute.clone(template)
        attribute.seat_id = seat_id
        attribute.save()

class Seat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "Seat"

    id              = Column(Identifier, primary_key=True)
    l0_id           = Column(String(255))
    name            = Column(Unicode(50), nullable=False, default=u"", server_default=u"")
    seat_no         = Column(String(255))
    stock_id        = Column(Identifier, ForeignKey('Stock.id'))

    venue_id        = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    row_l0_id       = Column(String(255), index=True)
    group_l0_id     = Column(String(255), index=True)

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
    adjacencies     = relationship("SeatAdjacency", secondary=Seat_SeatAdjacency.__table__, backref="seats")
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

    @staticmethod
    def create_from_template(template, venue_id, default_stock_id, convert_map):
        # create Seat
        seat = Seat.clone(template)
        seat.venue_id = venue_id
        if 'stock_id' in convert_map:
            seat.stock_id = convert_map['stock_id'][template.stock.id]
        else:
            seat.stock_id = default_stock_id
        for template_attribute in template.attributes:
            seat[template_attribute] = template[template_attribute]
        seat.save()

        # create SeatStatus
        SeatStatus.create_default(seat_id=seat.id)

        # create SeatIndex
        for template_seat_index in template.indexes:
            SeatIndex.create_from_template(
                template=template_seat_index,
                seat_id=seat.id,
                convert_map=convert_map
            )

        # create Seat_SeatAdjacency
        if template.adjacencies:
            seat_seat_adjacencies = []
            for template_adjacency in template.adjacencies:
                seat_seat_adjacencies.append({
                    'seat_adjacency_id':convert_map['seat_adjacency'][template_adjacency.id],
                    'seat_id':seat.id,
                })
            DBSession.execute(Seat_SeatAdjacency.__table__.insert(), seat_seat_adjacencies)

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
    def create_default(seat_id):
        seat_status = SeatStatus(status=SeatStatusEnum.Vacant.v, seat_id=seat_id)
        seat_status.save()

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

    @staticmethod
    def create_from_template(template, adjacency_set_id):
        adjacency = SeatAdjacency.clone(template)
        adjacency.adjacency_set_id = adjacency_set_id
        adjacency.save()
        return {template.id:adjacency.id}

class SeatAdjacencySet(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SeatAdjacencySet"
    id = Column(Identifier, primary_key=True)
    venue_id = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'))
    seat_count = Column(Integer, nullable=False)
    adjacencies = relationship("SeatAdjacency", backref='adjacency_set')
    venue = relationship("Venue", backref='adjacency_sets')

    @staticmethod
    def create_from_template(template, venue_id):
        adjacency_set = SeatAdjacencySet.clone(template)
        adjacency_set.venue_id = venue_id
        adjacency_set.save()

        convert_map = {}
        for template_adjacency in template.adjacencies:
            convert_map.update(
                SeatAdjacency.create_from_template(template_adjacency, adjacency_set.id)
            )

        return convert_map

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

class Performance(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Performance'

    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    code = Column(String(12))  # Organization.code(2桁) + Event.code(3桁) + 7桁(デフォルトはstart.onのYYMMDD+ランダム1桁)
    open_on = Column(DateTime)
    start_on = Column(DateTime)
    end_on = Column(DateTime)

    event_id = Column(Identifier, ForeignKey('Event.id'))

    stocks = relationship('Stock', backref='performance')
    product_items = relationship('ProductItem', backref='performance')
    venue = relationship('Venue', uselist=False, backref='performance')

    def add(self):
        BaseModel.add(self)

        if hasattr(self, 'original_id') and self.original_id:
            """
            Performanceのコピー時は以下のモデルをcloneする
              - Stock
                - ProductItem
            """
            template_performance = Performance.get(self.original_id)

            # create Stock - ProductItem
            for template_stock in template_performance.stocks:
                Stock.create_from_template(template=template_stock, performance_id=self.id)

        else:
            """
            Performanceの作成時は以下のモデルを自動生成する
              - Stock
                - ProductItem
            """
            # create default Stock
            Stock.create_default(self.event, performance_id=self.id)

    def save(self):
        BaseModel.save(self)

        """
        Performanceの作成/更新時は以下のモデルを自動生成する
        またVenueの変更があったら関連モデルを削除する
          - Venue
            - VenueArea
              - VenueArea_group_l0_id
            - SeatAdjacencySet
              - SeatAdjacency
            - SeatIndexType
            - Seat
              - SeatAttribute
              - SeatStatus
              - SeatIndex
              - SeatAdjacency_Seat
        """
        # create Venue - VenueArea, Seat - SeatAttribute
        original_performance_id = self.original_id if hasattr(self, 'original_id') else None
        if hasattr(self, 'create_venue_id') and self.venue_id:
            template_venue = Venue.get(self.venue_id)
            Venue.create_from_template(
                template=template_venue,
                performance_id=self.id,
                original_performance_id=self.original_id
            )

        # delete Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'delete_venue_id') and self.delete_venue_id:
            venue = Venue.get(self.delete_venue_id)
            venue.delete_cascade()

    def get_cms_data(self):
        start_on = isodate.datetime_isoformat(self.start_on) if self.start_on else ''
        end_on = isodate.datetime_isoformat(self.end_on) if self.end_on else ''
        open_on = isodate.datetime_isoformat(self.open_on) if self.open_on else ''

        # cmsでは日付は必須項目
        if not start_on and not self.deleted_at:
            raise Exception(u'パフォーマンスの日付を入力してください')

        data = {
            'id':self.id,
            'name':self.name,
            'venue':self.venue.name,
            'prefecture':self.venue.site.prefecture,
            'open_on':open_on,
            'start_on':start_on,
            'end_on':end_on,
            'tickets':list(set([pi.product.id for pi in self.product_items])),
        }
        if self.deleted_at:
            data['deleted'] = 'true'

        return data

    @classmethod
    def get(cls, id, organization_id=None, **kwargs):
        if organization_id:
            return Performance.filter(Performance.id==id).join(Event).filter(Event.organization_id==organization_id).first()
        return super(Performance, cls).get(id, **kwargs)

    @staticmethod
    def create_from_template(template, event_id):
        performance = Performance.clone(template)
        performance.event_id = event_id
        performance.original_id = template.id
        performance.venue_id = template.venue.id
        performance.create_venue_id = template.venue.id
        performance.save()

    @staticmethod
    def set_search_condition(query, form):
        sort = form.sort.data or 'id'
        direction = form.direction.data or 'desc'
        query = query.order_by('Performance.' + sort + ' ' + direction)

        condition = form.event_id.data
        if condition:
            query = query.filter(Performance.event_id==condition)

        return query

class Event(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Event'

    id = Column(Identifier, primary_key=True)
    code = Column(String(12))  # Organization.code(2桁) + 3桁英数字大文字のみ
    title = Column(String(1024))
    abbreviated_title = Column(String(1024))

    account_id = Column(Identifier, ForeignKey('Account.id'))
    account = relationship('Account', backref='events')

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref='events')

    performances = relationship('Performance', backref='event')
    stock_types = relationship('StockType', backref='event', order_by='StockType.display_order')
    stock_holders = relationship('StockHolder', backref='event')

    _first_performance = None
    _final_performance = None

    @property
    def accounts(self):
        return Account.filter().join(Account.stock_holders).filter(StockHolder.event_id==self.id).all()

    @property
    def sales_start_on(self):
        return SalesSegment.filter().with_entities(func.min(SalesSegment.start_at)).join(Product)\
                .filter(Product.event_id==self.id).scalar()

    @property
    def sales_end_on(self):
        return SalesSegment.filter().with_entities(func.min(SalesSegment.end_at)).join(Product)\
                .filter(Product.event_id==self.id).scalar()

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
    def get_owner_event(user_id):
        return Event.filter().join(Event.account).filter(Account.user_id==user_id).all()

    @staticmethod
    def get_client_event(user_id):
        return Event.filter().join(Event.stock_holders)\
                             .join(StockHolder.account)\
                             .filter(Account.user_id==user_id)\
                             .all()

    def get_accounts(self):
        return Account.filter().with_entities(Account.name).join(StockHolder)\
                .filter(Account.organization_id==self.organization_id)\
                .filter(Account.id==StockHolder.account_id)\
                .filter(StockHolder.event_id==self.id)\
                .distinct()

    def _get_self_cms_data(self):
        return {'id':self.id,
                'title':self.title,
                'subtitle':self.abbreviated_title,
                "organization_id": self.organization.id, 
                }

    def get_cms_data(self):
        '''
        CMSに連携するデータを生成する
        インターフェースのデータ構造は以下のとおり
        削除データには "deleted":"true" をいれる

        data = {
          "created_at": "2012-01-10T13:42:00+09:00",
          "updated_at": "2012-01-11T15:32:00+09:00",
          "organization_id": 1, 
          "events":[
            {
              "id":1,
              "title":"イベントタイトル",
              "subtitle":"サブタイトル",
              "start_on":"2012-03-15T19:00:00+09:00",,
              "end_on":"2012-03-15T19:00:00+09:00",,
              "performances":[
                "id":1,
                "title":"タイトル",
                "venue":"代々木体育館",
                "open_on":"2012-03-15T19:00:00+09:00",,
                "start_on":"2012-03-15T19:00:00+09:00",,
                "end_on":"2012-03-15T19:00:00+09:00",,
                "tickets":[1,2],
              ],
              "tickets":[
                {"id":1, "sale_id":1, "name":"A席大人", "seat_type":"A席", "price":5000, "display_order":1},
                {"id":2, "sale_id":2, "name":"B席大人", "seat_type":"B席", "price":3000, "display_order":2},
              ],
              "sales":[
                {"id":1, "name":"販売区分1", "start_on":~, "end_on":~, "seat_choice":true},
                {"id":2, "name":"販売区分2", "start_on":~, "end_on":~, "seat_choice":true},
              ],
            },
          ]
        }
        '''
        start_on = isodate.datetime_isoformat(self.first_start_on) if self.first_start_on else ''
        end_on = isodate.datetime_isoformat(self.final_start_on) if self.final_start_on else ''
        sales_start_on = isodate.datetime_isoformat(self.sales_start_on) if self.sales_start_on else ''
        sales_end_on = isodate.datetime_isoformat(self.sales_end_on) if self.sales_end_on else ''

        # cmsでは日付は必須項目
        if not (start_on and end_on) and not self.deleted_at:
            raise Exception(u'パフォーマンスが登録されていないイベントは送信できません')
        if not (sales_start_on and sales_end_on) and not self.deleted_at:
            raise Exception(u'販売期間が登録されていないイベントは送信できません')

        # 論理削除レコードも含めるので{Model}.query.filter()で取得している
        data = self._get_self_cms_data()
        data.update({
            'start_on':start_on,
            'end_on':end_on,
            'deal_open':sales_start_on,
            'deal_close':sales_end_on,
            'performances':[p.get_cms_data() for p in Performance.query.filter_by(event_id=self.id).all()],
            'tickets':[p.get_cms_data() for p in Product.find(event_id=self.id, include_deleted=True)],
            'sales':[s.get_cms_data() for s in SalesSegment.query.filter_by(event_id=self.id).all()],
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
              - SalesSegment
                - PaymentDeliveryMethodPair
              - Product
              - Performance
                - (この階層以下はPerformance.add()を参照)
            """
            template_event = Event.get(self.original_id)

            # 各モデルのコピー元/コピー先のidの対比表
            convert_map = {
                'stock_type':dict(),
                'stock_holder':dict(),
                'sales_segment':dict(),
                'product':dict(),
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

            # create SalesSegment - PaymentDeliveryMethodPair
            for template_sales_segment in template_event.sales_segments:
                convert_map['sales_segment'].update(
                    SalesSegment.create_from_template(template=template_sales_segment, event_id=self.id)
                )

            # create Product
            for template_product in template_event.products:
                convert_map['product'].update(
                    Product.create_from_template(template=template_product, event_id=self.id, convert_map=convert_map)
                )

            # create Performance
            for template_performance in template_event.performances:
                Performance.create_from_template(template=template_performance, event_id=self.id)

            '''
            Performance以下のコピーしたモデルにidを反映する
            '''
            performances = Performance.filter_by(event_id=self.id).with_entities(Performance.id).all()
            print performances
            for performance in performances:
                # 関連テーブルのstock_type_idを書き換える
                for old_id, new_id in convert_map['stock_type'].iteritems():
                    Stock.filter_by(stock_type_id=old_id)\
                        .filter_by(performance_id=performance.id)\
                        .update({'stock_type_id':new_id})

                # 関連テーブルのsales_holder_idを書き換える
                for old_id, new_id in convert_map['stock_holder'].iteritems():
                    Stock.filter_by(stock_holder_id=old_id)\
                        .filter_by(performance_id=performance.id)\
                        .update({'stock_holder_id':new_id})

                # 関連テーブルのproduct_idを書き換える
                for old_id, new_id in convert_map['product'].iteritems():
                    ProductItem.filter_by(product_id=old_id)\
                        .filter_by(performance_id=performance.id)\
                        .update({'product_id':new_id})

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

            stock_holder = StockHolder(
                name=u'自社',
                event_id=self.id,
                account_id=account.id,
                style={"text": u"自", "text_color": "#a62020"},
            )
            stock_holder.save()

class SalesSegmentKindEnum(StandardEnum):
    first_lottery   = u'最速抽選'
    early_lottery   = u'先行抽選'
    early_firstcome = u'先行先着'
    normal          = u'一般販売'
    added_sales     = u'追加販売'
    added_lottery   = u'追加抽選'
    vip             = u'関係者'
    sales_counter   = u'窓口販売'
    other           = u'その他'

class SalesSegment(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'SalesSegment'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    kind = Column(String(255))
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    upper_limit = Column(Integer)
    seat_choice = Column(Boolean, default=True)
    public = Column(Boolean, default=True)

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref='sales_segments')

    # membergroup_id = Column(Identifier, ForeignKey('MemberGroup.id'))
    # membergroup = relationship('MemberGroup', backref='salessegments')

    def delete(self):
        # 商品が割り当てられている場合は削除できない
        if self.product:
            raise Exception(u'商品の割当がある為、削除できません')

        # delete PaymentDeliveryMethodPair
        for pdmp in self.payment_delivery_method_pairs:
            pdmp.delete()

        super(SalesSegment, self).delete()

    def get_cms_data(self):
        start_at = isodate.datetime_isoformat(self.start_at) if self.start_at else ''
        end_at = isodate.datetime_isoformat(self.end_at) if self.end_at else ''
        data = {
            'id':self.id,
            'name':self.name,
            'kind':self.kind,
            'start_on':start_at,
            'end_on':end_at,
            'seat_choice':'true' if self.seat_choice else 'false',
        }
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    @staticmethod
    def create_from_template(template, event_id):
        sales_segment = SalesSegment.clone(template)
        sales_segment.event_id = event_id
        sales_segment.save()

        for template_pdmp in template.payment_delivery_method_pairs:
            PaymentDeliveryMethodPair.create_from_template(template=template_pdmp, sales_segment_id=sales_segment.id)

        return {template.id:sales_segment.id}

    @classmethod
    def copy_products(cls, from_, to_):
        products = DBSession.query(Product).filter(Product.sales_segment_id==from_.id).all()
        for product in products:
            new_product = Product(
                name=product.name,
                price=product.price,
                display_order=product.display_order,
                seat_stock_type_id=product.seat_stock_type_id,
                event_id=product.event_id,
                sales_segment=to_,
            )
            for product_item in product.items:
                new_product_item = ProductItem(
                    name=product_item.name,
                    price=product_item.price,
                    stock_id=product_item.stock_id,
                    quantity=product_item.quantity,
                    ticket_bundle_id=product_item.ticket_bundle_id,
                    product=new_product,
                    performance_id=product_item.performance_id,
                )

class PaymentDeliveryMethodPair(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentDeliveryMethodPair'

    id = Column(Identifier, primary_key=True)
    system_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    discount = Column(Numeric(precision=16, scale=2), nullable=False)
    discount_unit = Column(Integer)

    # 申込日から計算して入金できる期限、日数指定
    payment_period_days = Column(Integer, default=3)
    # 入金から発券できるまでの時間
    issuing_interval_days = Column(Integer, default=1)
    issuing_start_at = Column(DateTime, nullable=True)
    issuing_end_at = Column(DateTime, nullable=True)
    # 選択不可期間(Performance.start_onの何日前から利用できないか、日数指定)
    unavailable_period_days = Column(Integer, nullable=False, default=0)
    # 一般公開するか
    public = Column(Boolean, nullable=False, default=True)

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment', backref='payment_delivery_method_pairs')
    payment_method_id = Column(Identifier, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod', backref='payment_delivery_method_pairs')
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod', backref='payment_delivery_method_pairs')

    @staticmethod
    def create_from_template(template, sales_segment_id):
        pdmp = PaymentDeliveryMethodPair.clone(template)
        pdmp.sales_segment_id = sales_segment_id
        pdmp.save()

class PaymentMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

class FeeTypeEnum(StandardEnum):
    Once = (0, u'1件あたりの手数料')
    PerUnit = (1, u'1枚あたりの手数料')

class PaymentMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(2000))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(Identifier, ForeignKey('PaymentMethodPlugin.id'))
    payment_plugin = relationship('PaymentMethodPlugin', uselist=False)

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.payment_delivery_method_pairs:
            raise Exception(u'関連づけされた決済配送方法がある為、削除できません')

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
    delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)

    def delete(self):
        # 既に使用されている場合は削除できない
        if self.payment_delivery_method_pairs:
            raise Exception(u'関連づけされた決済配送方法がある為、削除できません')

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
                stock_holders = StockHolder.get_seller(performance.event)
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
    def create_from_template(template, stock_id, performance_id):
        product_item = ProductItem.clone(template)
        product_item.performance_id = performance_id
        product_item.stock_id = stock_id
        product_item.save()

class StockTypeEnum(StandardEnum):
    Seat = 0
    Other = 1

class StockType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'StockType'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    type = Column(Integer)  # @see StockTypeEnum
    display_order = Column(Integer, nullable=False, default=1)
    event_id = Column(Identifier, ForeignKey("Event.id"))
    quantity_only = Column(Boolean, default=False)
    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))
    stocks = relationship('Stock', backref=backref('stock_type', order_by='StockType.display_order'))

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

    def add(self):
        super(StockType, self).add()

        # create default Stock
        Stock.create_default(self.event, stock_type_id=self.id)

        # create default Product
        Product.create_default(stock_type=self)

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
    def create_from_template(template, event_id):
        stock_type = StockType.clone(template)
        stock_type.event_id = event_id
        stock_type.save()
        return {template.id:stock_type.id}

class StockHolder(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "StockHolder"
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

    event_id = Column(Identifier, ForeignKey('Event.id'))
    account_id = Column(Identifier, ForeignKey('Account.id'))

    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))
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
    def get_seller(event):
        return StockHolder.filter(StockHolder.event_id==event.id)\
                          .join(StockHolder.account)\
                          .filter(Account.user_id==event.organization.user_id)\
                          .order_by('StockHolder.id').all()

    @staticmethod
    def create_from_template(template, event_id):
        stock_holder = StockHolder.clone(template)
        stock_holder.event_id = event_id
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

    stock_status = relationship("StockStatus", uselist=False, backref='stock')

    def count_vacant_quantity(self):
        if self.stock_type and self.stock_type.quantity_only:
            from ticketing.cart.models import Cart, CartedProduct, CartedProductItem
            # 販売済みの座席数
            reserved_quantity = Stock.filter(Stock.id==self.id).join(Stock.product_items)\
                .join(ProductItem.ordered_product_items)\
                .join(OrderedProductItem.ordered_product)\
                .join(OrderedProduct.order)\
                .filter(Order.canceled_at==None)\
                .with_entities(func.sum(OrderedProduct.quantity)).scalar() or 0
            # Cartで確保されている座席数
            reserved_quantity += Stock.filter(Stock.id==self.id).join(Stock.product_items)\
                .join(ProductItem.carted_product_items)\
                .join(CartedProductItem.carted_product)\
                .join(CartedProduct.cart)\
                .filter(Cart.finished_at==None)\
                .with_entities(func.sum(CartedProduct.quantity)).scalar() or 0
            vacant_quantity = self.quantity - reserved_quantity
        else:
            vacant_quantity = Seat.filter(Seat.stock_id==self.id)\
                .join(SeatStatus)\
                .filter(Seat.id==SeatStatus.seat_id)\
                .filter(SeatStatus.status.in_([SeatStatusEnum.Vacant.v]))\
                .count()
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

    def delete(self):
        # 在庫が割り当てられている場合は削除できない
        if self.quantity > 0 or self.product_items:
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

class Product(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Product'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    display_order = Column(Integer, nullable=False, default=1)

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'), nullable=True)
    sales_segment = relationship('SalesSegment', uselist=False, backref=backref('product', order_by='Product.display_order'))

    seat_stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=True)
    seat_stock_type = relationship('StockType', uselist=False, backref=backref('product', order_by='Product.display_order'))

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref=backref('products', order_by='Product.display_order'))

    items = relationship('ProductItem', backref=backref('product', order_by='Product.display_order'))

    @staticmethod
    def find(performance_id=None, event_id=None, sales_segment_id=None, stock_id=None, include_deleted=False):
        query = Product.query
        if performance_id:
            query = query.join(Product.items).filter(ProductItem.performance_id==performance_id)
        if event_id:
            query = query.filter(Product.event_id==event_id)
        if sales_segment_id:
            query = query.filter(Product.sales_segment_id==sales_segment_id)
        if stock_id:
            if not performance_id:
                query = query.join(Product.items)
            query = query.filter(ProductItem.stock_id==stock_id)
        if not include_deleted:
            query = query.filter(Product.deleted_at==None)
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
        # 在庫が割り当てられている場合は削除できない
        if self.items:
            raise Exception(u'座席および席数の割当がある為、削除できません')

        super(Product, self).delete()

    def get_quantity_power(self, stock_type, performance_id):
        """ 数量倍率 """
        perform_items = ProductItem.query.filter(ProductItem.product==self).filter(ProductItem.performance_id==performance_id).all()
        return sum([pi.quantity for pi in perform_items if pi.stock.stock_type == stock_type])

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
            'sale_id':self.sales_segment_id,
            'seat_type':self.seat_type(),
            'display_order':self.display_order,
        }
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    def seat_type(self):
        return self.seat_stock_type.name if self.seat_stock_type else ''

    @staticmethod
    def create_from_template(template, event_id, convert_map):
        product = Product.clone(template)
        product.event_id = event_id
        product.seat_stock_type_id = convert_map['stock_type'][template.seat_stock_type_id]
        product.sales_segment_id = convert_map['sales_segment'][template.sales_segment_id]
        product.save()
        return {template.id:product.id}

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

    @staticmethod
    def create_from_template(template, seat_id, convert_map):
        seat_index = SeatIndex.clone(template)
        seat_index.seat_id = seat_id
        seat_index.seat_index_type_id = convert_map['seat_index_type'][template.seat_index_type_id]
        seat_index.save()

class OranizationTypeEnum(StandardEnum):
    Standard = 1

class Organization(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Organization"
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    code = Column(String(3))  # 2桁英字大文字のみ
    client_type = Column(Integer)
    contact_email = Column(String(255))
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))

    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship("User", uselist=False, backref=backref('organization', uselist=False))
    prefecture = Column(String(64), nullable=False, default=u'')

    status = Column(Integer)

orders_seat_table = Table("orders_seat", Base.metadata,
    Column("seat_id", Identifier, ForeignKey("Seat.id")),
    Column("OrderedProductItem_id", Identifier, ForeignKey("OrderedProductItem.id")),
)

class ShippingAddress(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ShippingAddress'
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User', backref='shipping_addresses')
    email = Column(String(255))
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
    email = Column(String(255))

    @property
    def full_name_kana(self):
        return u"%s %s" % (self.last_name_kana,  self.first_name_kana)

class Order(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Order'
    id = Column(Identifier, primary_key=True)
    user_id = Column(Identifier, ForeignKey("User.id"))
    user = relationship('User')
    shipping_address_id = Column(Identifier, ForeignKey("ShippingAddress.id"))
    shipping_address = relationship('ShippingAddress', backref='order')
    organization_id = Column(Identifier, ForeignKey("Organization.id"))
    ordered_from = relationship('Organization', backref='orders')

    items = relationship('OrderedProduct')
    total_amount = Column(Numeric(precision=16, scale=2), nullable=False)
    system_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)

    multicheckout_approval_no = Column(Unicode(255), doc=u"マルチ決済受領番号")

    payment_delivery_method_pair_id = Column(Identifier, ForeignKey("PaymentDeliveryMethodPair.id"))
    payment_delivery_pair = relationship("PaymentDeliveryMethodPair")

    paid_at = Column(DateTime, nullable=True, default=None)
    delivered_at = Column(DateTime, nullable=True, default=None)
    canceled_at = Column(DateTime, nullable=True, default=None)
    last_issued_at = Column(DateTime, nullable=True, default=None)

    order_no = Column(String(255))
    note = Column(UnicodeText, nullable=True, default=None)

    issued = Column(Boolean, nullable=False, default=False)
    issued_at = Column(DateTime, nullable=True, default=None, doc=u"印刷可能な情報伝達済み")
    printed_at = Column(DateTime, nullable=True, default=None, doc=u"実発券済み")

    performance_id = Column(Identifier, ForeignKey('Performance.id'))
    performance = relationship('Performance', backref="orders")

    _attributes = relationship("OrderAttribute", backref='order', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderAttribute(name=k, value=v))

    def is_issued(self):
        if self.issued_at:
            return True
        ## todo: eliminate query
        qs = OrderedProductItem.query.filter_by(deleted_at=None)\
            .filter(OrderedProduct.order_id==self.id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProductItem.issued_at==None)
        return qs.first() is None

    @classmethod
    def __declare_last__(cls):
        cls.queued = column_property(
                exists(select('*') \
                    .select_from(TicketPrintQueueEntry.__table__ \
                        .join(OrderedProductItem.__table__) \
                        .join(OrderedProduct.__table__)) \
                    .where(OrderedProduct.order_id==cls.id) \
                    .where(TicketPrintQueueEntry.processed_at==None)))

    @property
    def payment_plugin_id(self):
        return self.payment_delivery_pair.payment_method.payment_plugin_id

    @property
    def delivery_plugin_id(self):
        return self.payment_delivery_pair.delivery_method.delivery_plugin_id

    @property
    def sej_order(self):
        if not hasattr(self, "_sej_order"):
            self._sej_order = SejOrder.filter(SejOrder.order_id == self.order_no).first()
        return self._sej_order

    @property
    def status(self):
        if self.canceled_at:
            return 'refunded' if self.paid_at else 'canceled'
        elif self.delivered_at:
            return 'delivered'
        elif self.paid_at:
            return 'paid'
        else:
            return 'ordered'

    def cancel(self, request):
        # キャンセル済み、売上キャンセル済み、配送済みはキャンセルできない
        if self.status == 'canceled' or self.status == 'refunded' or self.status == 'delivered':
            return False

        '''
        決済方法ごとに払戻し処理
        '''
        ppid = self.payment_delivery_pair.payment_method.payment_plugin_id
        if not ppid:
            return False

        # クレジットカード決済
        if ppid == 1:
            # 入金済みなら決済をキャンセル
            if self.status == 'paid':
                # 売り上げキャンセル
                from ticketing.multicheckout import api as multi_checkout_api

                order_no = self.order_no
                if request.registry.settings.get('multicheckout.testing', False):
                    order_no = '%012d%02d' % (sensible_alnum_decode(order_no[2:12]), 0)
                organization = Organization.get(self.organization_id)
                request.registry.settings['altair_checkout3d.override_shop_name'] = organization.multicheckout_settings[0].shop_name
                
                multi_checkout_result = multi_checkout_api.checkout_sales_cancel(request, order_no)
                DBSession.add(multi_checkout_result)

                error_code = ''
                if multi_checkout_result.CmnErrorCd and multi_checkout_result.CmnErrorCd != '000000':
                    error_code = multi_checkout_result.CmnErrorCd
                elif multi_checkout_result.CardErrorCd and multi_checkout_result.CardErrorCd != '000000':
                    error_code = multi_checkout_result.CardErrorCd

                if error_code:
                    logger.error(u'クレジットカード決済のキャンセルに失敗しました。 %s' % error_code)
                    return False

                self.multi_checkout_approval_no = multi_checkout_result.ApprovalNo

        # 楽天あんしん決済
        elif ppid == 2:
            # ToDo
            pass

        # コンビニ決済 (セブンイレブン)
        elif ppid == 3:
            # 入金済みならキャンセル不可
            if self.status == 'paid':
                return False

            # 未入金ならコンビニ決済のキャンセル通知
            elif self.status == 'ordered':
                sej_order = SejOrder.query.filter_by(order_id=self.order_no).first()
                if sej_order and not sej_order.cancel_at:
                    settings = get_current_registry().settings
                    shop_id = settings.get('sej.shop_id', 0)
                    if sej_order.shop_id != shop_id:
                        logger.error(u'コンビニ決済(セブンイレブン)のキャンセルに失敗しました Invalid shop_id : %s' % shop_id)
                        return False

                    try:
                        request_cancel_order(
                            order_id=sej_order.order_id,
                            billing_number=sej_order.billing_number,
                            exchange_number=sej_order.exchange_number,
                            shop_id=shop_id,
                            secret_key=settings.get('sej.api_key'),
                            hostname=settings.get('sej.inticket_api_url')
                        )
                    except SejServerError, e:
                        logger.error(u'コンビニ決済(セブンイレブン)のキャンセルに失敗しました %s' % e)
                        return False

        # 窓口支払
        elif ppid == 4:
            pass

        # 在庫を戻す
        self.release()
        self.canceled_at = datetime.now()
        self.save()

        return True

    def release(self):
        # 在庫を解放する
        for product in self.ordered_products:
            product.release()

    def delivered(self):
        # 入金済みのみ配送済みにステータス変更できる
        if self.status == 'paid':
            self.delivered_at = datetime.now()
            self.save()
            return True
        else:
            return False

    @staticmethod
    def get(id, organization_id):
        return Order.filter_by(id=id, organization_id=organization_id).first()

    @classmethod
    def create_from_cart(cls, cart):
        order = cls()
        order.order_no = cart.order_no
        order.total_amount = cart.total_amount
        order.shipping_address = cart.shipping_address
        order.payment_delivery_pair = cart.payment_delivery_pair
        order.system_fee = cart.system_fee
        order.transaction_fee = cart.transaction_fee
        order.delivery_fee = cart.delivery_fee
        order.performance = cart.performance

        for product in cart.products:
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

    @staticmethod
    def set_search_condition(query, form):
        sort = form.sort.data or 'id'
        direction = form.direction.data or 'desc'
        query = query.order_by('Order.' + sort + ' ' + direction)

        condition = form.order_no.data
        if condition:
            query = query.filter(Order.order_no==condition)
        condition = form.performance_id.data
        if condition:
            query = query.filter(Order.performance_id==condition)
        condition = form.event_id.data
        if condition:
            query = query.join(Order.performance).filter(Performance.event_id==condition)
        condition = form.ordered_from.data
        if condition:
            query = query.filter(Order.created_at>=condition)
        condition = form.ordered_to.data
        if condition:
            query = query.filter(Order.created_at<=condition)
        condition = form.payment_method.data
        if condition:
            query = query.join(Order.payment_delivery_pair)
            query = query.join(PaymentMethod)
            query = query.filter(PaymentMethod.payment_plugin_id.in_(condition))
        condition = form.delivery_method.data
        if condition:
            query = query.join(Order.payment_delivery_pair)
            query = query.join(DeliveryMethod)
            query = query.filter(DeliveryMethod.delivery_plugin_id.in_(condition))
        condition = form.status.data
        if condition:
            status_cond = []
            if 'refunded' in condition:
                status_cond.append(and_(Order.canceled_at!=None, Order.paid_at!=None))
            if 'canceled' in condition:
                status_cond.append(and_(Order.canceled_at!=None, Order.paid_at==None))
            if 'delivered' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.delivered_at!=None))
            if 'paid' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.paid_at!=None, Order.delivered_at==None))
            if 'ordered' in condition:
                status_cond.append(and_(Order.canceled_at==None, Order.paid_at==None, Order.delivered_at==None))
            if 'issued' in condition:
                status_cond.append(Order.issued==True)
            if 'unissued' in condition:
                status_cond.append(Order.issued==False)
            if status_cond:
                query = query.filter(or_(*status_cond))
        condition = form.tel.data
        if condition:
            query = query.join(Order.shipping_address).filter(or_(ShippingAddress.tel_1==condition, ShippingAddress.tel_2==condition))
        condition = form.name.data
        if condition:
            query = query.join(Order.shipping_address).filter(ShippingAddress.last_name + ShippingAddress.first_name==condition)
        condition = form.member_id.data
        if condition:
            query = query.join(Order.user).join(User.user_credential).filter(UserCredential.auth_identifier==condition)
        condition = form.start_on_from.data
        if condition:
            query = query.join(Order.performance).filter(Performance.start_on>=condition)
        condition = form.start_on_to.data
        if condition:
            query = query.join(Order.performance).filter(Performance.start_on<=condition)
        return query


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
    id = Column(Identifier, primary_key=True)
    order_id = Column(Identifier, ForeignKey("Order.id"))
    order = relationship('Order', backref='ordered_products')
    product_id = Column(Identifier, ForeignKey("Product.id"))
    product = relationship('Product', backref='ordered_products')
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    quantity = Column(Integer)

    def release(self):
        # 在庫を解放する
        for item in self.ordered_product_items:
            item.release()

    @property
    def seats(self):
        return sorted(itertools.chain.from_iterable(i.seatdicts for i in self.ordered_product_items),
            key=operator.itemgetter('l0_id'))

class OrderedProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'OrderedProductItem'
    id = Column(Identifier, primary_key=True)
    ordered_product_id = Column(Identifier, ForeignKey("OrderedProduct.id"))
    ordered_product = relationship('OrderedProduct', backref='ordered_product_items')
    product_item_id = Column(Identifier, ForeignKey("ProductItem.id"))
    product_item = relationship('ProductItem', backref='ordered_product_items')
    issued_at = Column(DateTime, nullable=True, default=None)
    printed_at = Column(DateTime, nullable=True, default=None)
#    seat_id = Column(Identifier, ForeignKey('Seat.id'))
#    seat = relationship('Seat')
    seats = relationship("Seat", secondary=orders_seat_table, backref='ordered_product_items')
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    _attributes = relationship("OrderedProductAttribute", backref='ordered_product_item', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('_attributes', 'value', creator=lambda k, v: OrderedProductAttribute(name=k, value=v))

    # 実際の購入数
    quantity = Column(Integer, nullable=False, default=1, server_default='1')

    @property
    def seat_statuses_for_update(self):
      return DBSession.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in self.seats])).with_lockmode('update').all()

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
                raise InvalidStockStateError("This order is associated with a seat (id=%d, status=%d) that is not marked ordered" % seat_status.seat_id, seat_status.status)
            else:
                logger.info('setting status of seat (id=%d, status=%d) to Vacant (%d)' % (seat_status.seat_id, seat_status.status, int(SeatStatusEnum.Vacant)))
                seat_status.status = int(SeatStatusEnum.Vacant)

        # 在庫数を戻す
        if self.product_item.stock.stock_type.quantity_only:
            release_quantity = self.quantity
        else:
            release_quantity = len(self.seats)
        logger.info('release stock id=%s quantity=%d' % (self.product_item.stock_id, release_quantity))
        query = StockStatus.__table__.update().values(
            {'quantity': StockStatus.quantity + release_quantity}
        ).where(StockStatus.stock_id==self.product_item.stock_id)
        DBSession.bind.execute(query)

    @property
    def seatdicts(self):
        return ({'name': s.name, 'l0_id': s.l0_id}
                for s in self.seats)

    def is_issued(self):
        return self.issued_at or self.tokens == [] or all(token.issued_at for token in self.tokens)

    @property
    def issued_at_status(self):
        total = len(self.tokens)
        issued_count = len([i for i in self.tokens if i.issued_at])
        return dict(issued=issued_count, total=total)
        
class OrderedProductItemToken(Base,BaseModel, LogicallyDeleted):
    __tablename__ = "OrderedProductItemToken"
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

    FLAG_ALWAYS_REISSUABLE = 1

    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=True)
    organization = relationship('Organization', uselist=False, backref=backref('ticket_templates'))
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='tickets')
    ticket_format_id = Column(Identifier, ForeignKey('TicketFormat.id', ondelete='CASCADE'), nullable=False)
    ticket_format = relationship('TicketFormat', uselist=False, backref='tickets')
    name = Column(Unicode(255), nullable=False, default=u'')
    flags = Column(Integer, nullable=False, default=0)
    data = Column(MutationDict.as_mutable(JSONEncodedDict(65536)))

    @classmethod
    def templates_query(cls):
        return cls.filter_by(event_id=None)

    @property
    def drawing(self):
        return self.data["drawing"]

    def create_event_bound(self, event):
        new_object = self.__class__.clone(self)
        new_object.event_id = event.id
        return new_object

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

    @property
    def drawing(self):
        return self.data["drawing"]

    @classmethod
    def enqueue(self, operator, ticket, data, summary, ordered_product_item=None, seat=None):
        DBSession.add(TicketPrintQueueEntry(operator=operator, ticket=ticket, data=data, summary=summary, ordered_product_item=ordered_product_item))

    @classmethod
    def peek(self, operator, ticket_format_id, order_id=None):
        q = DBSession.query(TicketPrintQueueEntry) \
            .filter_by(processed_at=None, operator=operator) \
            .filter(Ticket.ticket_format_id==ticket_format_id) \
            .join(OrderedProductItem) \
            .join(OrderedProduct)
        if order_id is not None:
            q = q.filter(OrderedProduct.order_id==order_id)
        q = q.order_by(asc(OrderedProduct.id), desc(self.created_at))
        return q.all()

    @classmethod
    def dequeue(self, ids):
        entries = DBSession.query(TicketPrintQueueEntry) \
            .with_lockmode("update") \
            .outerjoin(TicketPrintQueueEntry.ordered_product_item) \
            .outerjoin(OrderedProductItem.ordered_product) \
            .outerjoin(OrderedProduct.order) \
            .filter(TicketPrintQueueEntry.id.in_(ids)) \
            .filter(TicketPrintQueueEntry.processed_at == None) \
            .all()
        if len(entries) == 0:
            return []
        now = datetime.now()
        for entry in entries:
            entry.processed_at = now
            order = entry.ordered_product_item.ordered_product.order
            if not (entry.ticket.flags & Ticket.FLAG_ALWAYS_REISSUABLE):
                entry.ordered_product_item.ordered_product.order.isseud = True
            order.last_issued_at = now
            order.issued = True
        return entries

from ..operators.models import Operator

class TicketBundle(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "TicketBundle"
    id = Column(Identifier, primary_key=True)
    name = Column(Unicode(255), default=u"", nullable=False)
    event_id = Column(Identifier, ForeignKey('Event.id', ondelete='CASCADE'))
    event = relationship('Event', uselist=False, backref='ticket_bundles')
    operator_id = Column(Identifier, ForeignKey('Operator.id'))
    operator = relationship('Operator', uselist=False)
    attributes_ = relationship("TicketBundleAttribute", backref='bundle', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    attributes = association_proxy('attributes_', 'value', creator=lambda k, v: SeatAttribute(name=k, value=v))
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


class TicketPrintHistory(Base, BaseModel, WithTimestamp):
    __tablename__ = "TicketPrintHistory"
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
    ticket_id = Column(Identifier, ForeignKey('Ticket.id'), nullable=False)
    ticket = relationship('Ticket')

    def before_insert_or_update(self):
        if self.order_id is None and self.item_token_id is None and \
            self.ordered_product_item_id is None:
            raise DomainConstraintError('any one of order_id, item_token_id, ordered_product_item_id must have a non-null value')

for event_kind in ['before_insert', 'before_update']:
    event.listen(TicketPrintHistory, event_kind, lambda mapper, conn, target: target.before_insert_or_update())

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
        DBSession.add(TicketPrintQueue(data = data, operator = operator))

    @classmethod
    def dequeue_all(self, operator):
        '''
        '''
        return TicketPrintQueue.filter_by(deleted_at = None, operator = operator).order_by('created_at desc').all()

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
    CompleteMail = 1
    PurchaseCancelMail = 2

MailTypeLabels = (u"購入完了メール", u"購入キャンセルメール")
assert(len(list(MailTypeEnum)) == len(MailTypeLabels))
MailTypeChoices = [(str(e), label)for e, label in zip(sorted(MailTypeEnum), MailTypeLabels)]


class Host(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Host'

    query = DBSession.query_property()

    id = Column(Identifier, primary_key=True)
    host_name = Column(Unicode(255), unique=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', backref="hosts")
