# encoding: utf-8
from sqlalchemy import Table, Column, ForeignKey, ForeignKeyConstraint, func
from sqlalchemy.types import Boolean, BigInteger, Integer, Float, String, Date, DateTime, Numeric, Unicode
from sqlalchemy.orm import join, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from ticketing.models import *
from ticketing.users.models import User

seat_seat_adjacency_table = Table(
    "Seat_SeatAdjacency", Base.metadata,
    Column('seat_id', Identifier, ForeignKey("Seat.id", ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('seat_adjacency_id', Identifier, ForeignKey("SeatAdjacency.id", ondelete='CASCADE'), primary_key=True, nullable=False)
    )

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

class VenueArea_group_l0_id(Base):
    __tablename__   = "VenueArea_group_l0_id"
    venue_id = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    group_l0_id = Column(String(255), ForeignKey('Seat.group_l0_id', onupdate=None, ondelete=None), primary_key=True, nullable=True)
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

    @staticmethod
    def create_from_template(template, performance_id):
        # create Venue
        venue = Venue.clone(template)
        venue.original_venue_id = template.id
        venue.performance_id = performance_id
        venue.save()

        # create VenueArea
        for template_area in template.areas:
            VenueArea.create_from_template(template=template_area, venue_id=venue.id)

        # create Seat
        default_stock = Stock.get_default(performance_id=performance_id)
        for template_seat in template.seats:
            Seat.create_from_template(template=template_seat, venue_id=venue.id, stock_id=default_stock.id)

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
    stock_id        = Column(Identifier, ForeignKey('Stock.id'))

    venue_id        = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)
    group_l0_id     = Column(String(255), index=True)

    venue           = relationship("Venue", backref='seats')
    stock           = relationship("Stock", backref='seats')

    attributes_      = relationship("SeatAttribute", backref='seat', collection_class=attribute_mapped_collection('name'), cascade='all,delete-orphan')
    areas           = relationship("VenueArea",
                                   primaryjoin=lambda:and_(
                                        Seat.venue_id==VenueArea_group_l0_id.venue_id,
                                        Seat.group_l0_id==VenueArea_group_l0_id.group_l0_id),
                                   secondary=VenueArea_group_l0_id.__table__,
                                   secondaryjoin=VenueArea_group_l0_id.venue_area_id==VenueArea.id,
                                   backref="seats")
    adjacencies     = relationship("SeatAdjacency", secondary=seat_seat_adjacency_table, backref="seats")
    status_ = relationship('SeatStatus', uselist=False, backref='seat') # 1:1

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
    def create_from_template(template, venue_id, stock_id):
        # create Seat
        seat = Seat.clone(template)
        seat.venue_id = venue_id
        seat.stock_id = stock_id
        seat.save()

        # create SeatAttribute
        for template_attribute in template.attributes:
            SeatAttribute.create_from_template(template=template_attribute, seat_id=seat.id)

        # create SeatStatus
        SeatStatus.create_default(seat_id=seat.id)

    def delete_cascade(self):
        # delete SeatStatus
        seat_status = SeatStatus.filter_by(seat_id=self.id).first()
        if seat_status:
            seat_status.delete()

        # delete SeatAttribute
        for attribute in self.attributes:
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

class SeatAdjacency(Base):
    __tablename__ = "SeatAdjacency"
    query = DBSession.query_property()
    id = Column(Identifier, primary_key=True)
    adjacency_set_id = Column(Identifier, ForeignKey('SeatAdjacencySet.id', ondelete='CASCADE'))

class SeatAdjacencySet(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SeatAdjacencySet"
    id = Column(Identifier, primary_key=True)
    venue_id = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'))
    seat_count = Column(Integer, nullable=False)
    adjacencies = relationship("SeatAdjacency", backref='adjacency_set')
    venue = relationship("Venue", backref='adjacency_sets')

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

    @property
    def account_type_label(self):
        for account_type in AccountTypeEnum:
            if account_type.v[0] == self.account_type:
                return account_type.v[1]
        return

    @staticmethod
    def get_by_organization_id(id):
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
            - Seat
              - SeatAttribute
              - SeatStatus
        """
        # create Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'create_venue_id') and self.venue_id:
            template_venue = Venue.get(self.venue_id)
            Venue.create_from_template(template=template_venue, performance_id=self.id)

        # delete Venue - VenueArea, Seat - SeatAttribute
        if hasattr(self, 'delete_venue_id') and self.delete_venue_id:
            venue = Venue.get(self.delete_venue_id)
            venue.delete_cascade()

    def get_cms_data(self):
        start_on = isodate.datetime_isoformat(self.start_on) if self.start_on else ''
        end_on = isodate.datetime_isoformat(self.end_on) if self.end_on else ''
        open_on = isodate.datetime_isoformat(self.open_on) if self.open_on else ''

        # cmsでは日付は必須項目
        if not (start_on and end_on and open_on) and not self.deleted_at:
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
    stock_types = relationship('StockType', backref='event')
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
                {"id":1, "sale_id":1, "name":"A席大人", "seat_type":"A席", "price":5000},
                {"id":2, "sale_id":2, "name":"B席大人", "seat_type":"B席", "price":3000},
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

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref='sales_segments')

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

class PaymentDeliveryMethodPair(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentDeliveryMethodPair'

    id = Column(Identifier, primary_key=True)
    system_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    transaction_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    delivery_fee = Column(Numeric(precision=16, scale=2), nullable=False)
    discount = Column(Numeric(precision=16, scale=2), nullable=False)
    discount_unit = Column(Integer)

    # 申し込日から計算して入金できる期限　日付指定
    payment_period_days = Column(Integer, default=3)
    # 入金から発券できるまでの時間
    issuing_interval_days = Column(Integer, default=1)
    issuing_start_at = Column(DateTime, nullable=True)
    issuing_end_at = Column(DateTime, nullable=True)

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'))
    sales_segment = relationship('SalesSegment', backref='payment_delivery_method_pairs')
    payment_method_id = Column(Identifier, ForeignKey('PaymentMethod.id'))
    payment_method = relationship('PaymentMethod')
    delivery_method_id = Column(Identifier, ForeignKey('DeliveryMethod.id'))
    delivery_method = relationship('DeliveryMethod')

class PaymentMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

class DeliveryMethodPlugin(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethodPlugin'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))

class FeeTypeEnum(StandardEnum):
    Once = (0, u'1回あたりの手数料')
    PerUnit = (1, u'1件あたりの手数料')

class PaymentMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PaymentMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False, backref='payment_method_list')
    payment_plugin_id = Column(Identifier, ForeignKey('PaymentMethodPlugin.id'))
    payment_plugin = relationship('PaymentMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return PaymentMethod.filter(PaymentMethod.organization_id==id).all()

class DeliveryMethod(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'DeliveryMethod'
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    fee = Column(Numeric(precision=16, scale=2), nullable=False)
    fee_type = Column(Integer, nullable=False, default=FeeTypeEnum.Once.v[0])

    organization_id = Column(Identifier, ForeignKey('Organization.id'))
    organization = relationship('Organization', uselist=False , backref='delivery_method_list')
    delivery_plugin_id = Column(Identifier, ForeignKey('DeliveryMethodPlugin.id'))
    delivery_plugin = relationship('DeliveryMethodPlugin', uselist=False)

    @staticmethod
    def get_by_organization_id(id):
        return DeliveryMethod.filter(DeliveryMethod.organization_id==id).all()

buyer_condition_set_table =  Table('BuyerConditionSet', Base.metadata,
    Column('id', Identifier, primary_key=True),
    Column('buyer_condition_id', Identifier, ForeignKey('BuyerCondition.id')),
    Column('product_id', Identifier, ForeignKey('Product.id'))
)

class BuyerCondition(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'BuyerCondition'
    id = Column(Identifier, primary_key=True)

    member_ship_id = Column(Identifier, ForeignKey('MemberShip.id'))
    member_ship   = relationship('MemberShip')
    '''
     Any Conditions.....
    '''

class ProductItem(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ProductItem'
    id = Column(Identifier, primary_key=True)
    item_type = Column(Integer)
    price = Column(Numeric(precision=16, scale=2), nullable=False)

    product_id = Column(Identifier, ForeignKey('Product.id'))
    performance_id = Column(Identifier, ForeignKey('Performance.id'))

    stock_id = Column(Identifier, ForeignKey('Stock.id'))
    stock = relationship("Stock", backref="product_items")

    quantity = Column(Integer, nullable=False, default=1, server_default='1')

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

    @staticmethod
    def create_default(product):
        '''
        ProductIetmを自動生成する
          - Product追加時に、座席(StockType.is_seatが真)のProductItemをPerformance数だけ生成
          - Performance追加時に、StockType × Product分のProductItemを生成
        '''
        if not product.seat_stock_type.is_seat:
            return

        for performance in product.event.performances:
            product_item = [item for item in product.items if item.performance_id == performance.id]
            if not product_item:
                stock_holders = StockHolder.get_seller(performance.event)
                for stock_holder in stock_holders:
                    stock = Stock.filter_by(performance_id=performance.id)\
                                 .filter_by(stock_type_id=product.seat_stock_type_id)\
                                 .filter_by(stock_holder_id=stock_holder.id)\
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
    event_id = Column(Identifier, ForeignKey("Event.id"))
    quantity_only = Column(Boolean, default=False)
    style = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))
    stocks = relationship('Stock', backref='stock_type')

    @property
    def is_seat(self):
        return self.type == StockTypeEnum.Seat.v

    def add(self):
        super(StockType, self).add()

        # create default Stock
        Stock.create_default(self.event, stock_type_id=self.id)

        # create default Product
        Product.create_default(stock_type=self)

    def num_seats(self, performance_id=None):
        # 同一Performanceの同一StockTypeにおけるStock.quantityの合計
        query = Stock.filter_by(stock_type_id=self.id).with_entities(func.sum(Stock.quantity))
        if performance_id:
            query = query.filter_by(performance_id==performance_id)
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

    def stocks_by_performance(self, performance_id):
        def performance_filter(stock):
            return (stock.performance_id == performance_id)
        return filter(performance_filter, self.stocks)

    @staticmethod
    def get_seller(event):
        return StockHolder.filter(StockHolder.event_id==event.id)\
                          .join(StockHolder.account)\
                          .filter(Account.user_id==event.organization.user_id)\
                          .all()

# stock based on quantity
class Stock(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Stock"
    id = Column(Identifier, primary_key=True)
    quantity = Column(Integer)
    performance_id = Column(Identifier, ForeignKey('Performance.id'), nullable=False)
    stock_holder_id = Column(Identifier, ForeignKey('StockHolder.id'), nullable=True)
    stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=True)

    stock_status = relationship("StockStatus", uselist=False, backref='stock')

    def save(self):
        # 登録時にStockStatusを作成
        case_add = False if hasattr(self, 'id') and self.id else True
        super(Stock, self).save()

        if case_add:
            stock_status = StockStatus(stock_id=self.id, quantity=self.quantity)
            stock_status.save()

    @staticmethod
    def get_default(performance_id):
        return Stock.filter_by(performance_id=performance_id).filter_by(stock_type_id=None).first()

    @staticmethod
    def create_default(event, performance_id=None, stock_type_id=None, stock_holder_id=None):
        '''
        初期状態のStockを生成する
          - デフォルト値となる"未選択"のStock
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

        # Performance × StockType × StockHolder分のStockを生成
        created_stock_types = []
        for performance in performances:
            for stock_type in stock_types:
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

        # ProductItemを生成
        for stock_type_id in created_stock_types:
            products = Product.filter(Product.event_id==event.id)\
                              .filter(Product.seat_stock_type_id==stock_type_id)\
                              .all()
            for product in products:
                ProductItem.create_default(product)

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

    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id'), nullable=True)
    sales_segment = relationship('SalesSegment', uselist=False, backref='product')

    seat_stock_type_id = Column(Identifier, ForeignKey('StockType.id'), nullable=True)
    seat_stock_type = relationship('StockType', uselist=False, backref='product')

    event_id = Column(Identifier, ForeignKey('Event.id'))
    event = relationship('Event', backref='products')

    items = relationship('ProductItem', backref='product')

    @staticmethod
    def find(performance_id=None, event_id=None, sales_segment_id=None, include_deleted=False):
        query = Product.query
        if performance_id:
            query = query.join(Product.items).filter(ProductItem.performance_id==performance_id)
        if event_id:
            query = query.filter(Product.event_id==event_id)
        if sales_segment_id:
            query = query.filter(Product.sales_segment_id==sales_segment_id)
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
                price=0,  #TODO: SalesSegmentのデフォルト値はどうするか
                event_id=stock_type.event_id,
                seat_stock_type_id=stock_type.id
            )
            product.save()

            # Performance数分のProductItemを生成
            ProductItem.create_default(product=product)

    def add(self):
        super(Product, self).add()

        # Performance数分のProductItemを生成
        ProductItem.create_default(product=self)

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
        }
        if self.deleted_at:
            data['deleted'] = 'true'
        return data

    def seat_type(self):
        name = ProductItem.filter_by(product_id=self.id)\
                          .join(Stock).join(StockType)\
                          .filter(StockType.type==StockTypeEnum.Seat.v)\
                          .with_entities(StockType.name).first()
        return name if name else ''

class SeatIndexType(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__  = "SeatIndexType"
    id             = Column(Identifier, primary_key=True)
    venue_id       = Column(Identifier, ForeignKey('Venue.id', ondelete='CASCADE'))
    name           = Column(String(255), nullable=False)
    seat_indexes   = relationship('SeatIndex', backref='seat_index_type')

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

