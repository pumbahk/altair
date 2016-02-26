# -*- coding:utf-8 -*-
from collections import OrderedDict

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    DateTime,
    or_,
    and_,
)

from sqlalchemy import orm
from altair.models import (
    Identifier,
    WithTimestamp,
)

from altair.app.ticketing.models import (
    Base,
    BaseModel,
    LogicallyDeleted,
    DBSession,
)

from altair.app.ticketing.core.models import (
    Event,
    Performance,
    Venue,
    PaymentDeliveryMethodPair,
    PaymentMethod,
    DeliveryMethod,
    ShippingAddress,
    ReportFrequencyEnum,
    Organization,
    ReportRecipient,
)
from altair.app.ticketing.orders.models import (
    Order,
    )
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    LotEntryWish,
    LotElectWork,
    LotRejectWork,
)
from altair.app.ticketing.sej.models import (
    SejOrder,
)
from altair.multicheckout.models import (
    MultiCheckoutOrderStatus,
)

other_electing = LotElectWork.__table__.alias()

class LotWishSummary(Base):
    __mapper_args__ = dict(
        include_properties=[
            LotEntry.__table__.c.organization_id,
            LotEntry.__table__.c.channel,
            LotEntryWish.__table__.c.id,
            LotEntryWish.__table__.c.created_at,
            LotEntry.__table__.c.entry_no,
            LotEntry.__table__.c.closed_at,
            LotEntry.__table__.c.ordered_mail_sent_at,
            LotEntryWish.__table__.c.wish_order,
            LotEntryWish.__table__.c.canceled_at,
            LotEntryWish.__table__.c.withdrawn_at,
            LotEntryWish.__table__.c.elected_at,
            LotEntryWish.__table__.c.rejected_at,
            PaymentMethod.__table__.c.name.label('payment_method_name'),
            PaymentMethod.__table__.c.payment_plugin_id,
            DeliveryMethod.__table__.c.name.label('delivery_method_name'),
            DeliveryMethod.__table__.c.delivery_plugin_id,
            Performance.__table__.c.name.label('performance_name'),
            Performance.__table__.c.code.label('performance_code'),
            Event.__table__.c.title.label('event_title'),
            Lot.__table__.c.id.label('lot_id'),
            LotElectWork.__table__.c.id.label('lot_elect_work_id'),
            LotElectWork.__table__.c.error.label('lot_elect_work_error'),
            other_electing.c.id.label('lot_other_elect_work_id'),
            LotRejectWork.__table__.c.id.label('lot_reject_work_id'),
            ShippingAddress.__table__.c.id.label('shipping_address_id'),
            ShippingAddress.__table__.c.last_name.label('shipping_address_last_name'),
            ShippingAddress.__table__.c.first_name.label('shipping_address_first_name'),
            ShippingAddress.__table__.c.last_name_kana.label('shipping_address_last_name_kana'),
            ShippingAddress.__table__.c.first_name_kana.label('shipping_address_first_name_kana'),
            ShippingAddress.__table__.c.prefecture.label('shipping_address_prefecture'),
            ShippingAddress.__table__.c.city.label('shipping_address_city'),
            ShippingAddress.__table__.c.address_1.label('shipping_address_address_1'),
            ShippingAddress.__table__.c.address_2.label('shipping_address_address_2'),
            ShippingAddress.__table__.c.tel_1.label('shipping_address_tel_1'),
            ShippingAddress.__table__.c.tel_2.label('shipping_address_tel_2'),
            ShippingAddress.__table__.c.email_1.label('shipping_address_email_1'),
            ShippingAddress.__table__.c.email_2.label('shipping_address_email_2'),
            MultiCheckoutOrderStatus.__table__.c.Status,
            SejOrder.__table__.c.billing_number,
            SejOrder.__table__.c.exchange_number,
        ],
        primary_key=[
            LotEntryWish.__table__.c.id
        ])



    id = LotEntryWish.id
    created_at = LotEntryWish.__table__.c.created_at
    organization_id = LotEntry.__table__.c.organization_id
    organization = orm.relationship('Organization', primaryjoin=(organization_id==Organization.id))
    channel = LotEntry.__table__.c.channel
    entry_no = LotEntry.__table__.c.entry_no
    wish_order = LotEntryWish.__table__.c.wish_order
    performance_name = Performance.__table__.c.name
    performance_code = Performance.__table__.c.code
    performance_start_on = Performance.__table__.c.start_on
    performance_end_on = Performance.__table__.c.end_on
    performance_open_on = Performance.__table__.c.open_on
    payment_method_name = PaymentMethod.__table__.c.name
    delivery_method_name = DeliveryMethod.__table__.c.name
    event_title = Event.__table__.c.title
    lot_id = Lot.__table__.c.id
    closed_at = LotEntry.__table__.c.closed_at
    lot_elect_work_id = LotElectWork.__table__.c.id
    lot_elect_work_error = LotElectWork.__table__.c.error
    lot_other_elect_work_id = other_electing.c.id
    lot_reject_work_id = LotRejectWork.__table__.c.id
    shipping_address_id = ShippingAddress.__table__.c.id
    shipping_address_last_name = ShippingAddress.__table__.c.last_name
    shipping_address_first_name = ShippingAddress.__table__.c.first_name
    shipping_address_last_name_kana = ShippingAddress.__table__.c.last_name_kana
    shipping_address_first_name_kana = ShippingAddress.__table__.c.first_name_kana
    shipping_address_prefecture = ShippingAddress.__table__.c.prefecture
    shipping_address_city = ShippingAddress.__table__.c.city
    shipping_address_address_1 = ShippingAddress.__table__.c.address_1
    shipping_address_address_2 = ShippingAddress.__table__.c.address_2
    shipping_address_tel_1 = ShippingAddress.__table__.c.tel_1
    shipping_address_tel_2 = ShippingAddress.__table__.c.tel_2
    shipping_address_email_1 = ShippingAddress.__table__.c.email_1
    shipping_address_email_2 = ShippingAddress.__table__.c.email_2
    venue_name = Venue.__table__.c.name
    Status = MultiCheckoutOrderStatus.__table__.c.Status
    sej_billing_number = SejOrder.__table__.c.billing_number
    sej_exchange_number = SejOrder.__table__.c.exchange_number


    __table__ = LotEntryWish.__table__.join(
        LotEntry.__table__,
        and_(LotEntry.id==LotEntryWish.lot_entry_id,
             LotEntry.deleted_at==None),
    ).join(
        ShippingAddress.__table__,
        and_(ShippingAddress.id==LotEntry.shipping_address_id,
             ShippingAddress.deleted_at==None),
    ).join(
        Lot.__table__,
        and_(Lot.id==LotEntry.lot_id,
             Lot.deleted_at==None),
    ).join(
        Event.__table__,
        and_(Lot.event_id==Event.id,
             Event.deleted_at==None),
    ).join(
        Performance.__table__,
        and_(LotEntryWish.performance_id==Performance.id,
             Performance.deleted_at==None),
    ).join(
        Venue.__table__,
        and_(Venue.performance_id==Performance.id,
             Venue.deleted_at==None),
    ).join(
        PaymentDeliveryMethodPair.__table__,
        and_(PaymentDeliveryMethodPair.id==LotEntry.payment_delivery_method_pair_id,
             PaymentDeliveryMethodPair.deleted_at==None),
    ).join(
        PaymentMethod.__table__,
        and_(PaymentMethod.id==PaymentDeliveryMethodPair.payment_method_id,
             PaymentMethod.deleted_at==None),
    ).join(
        DeliveryMethod.__table__,
        and_(DeliveryMethod.id==PaymentDeliveryMethodPair.delivery_method_id,
             DeliveryMethod.deleted_at==None),
    ).outerjoin(
        LotElectWork.__table__,
        and_(LotElectWork.lot_entry_no==LotEntry.entry_no,
             LotElectWork.wish_order==LotEntryWish.wish_order),
    ).outerjoin(
        other_electing,
        and_(other_electing.c.lot_entry_no==LotEntry.entry_no,
             other_electing.c.wish_order!=LotEntryWish.wish_order),
    ).outerjoin(
        LotRejectWork.__table__,
        LotRejectWork.lot_entry_no==LotEntry.entry_no,
    ).outerjoin(
        MultiCheckoutOrderStatus.__table__,
        and_(MultiCheckoutOrderStatus.OrderNo==LotEntry.entry_no,
                 MultiCheckoutOrderStatus.Status!=None),
    ).outerjoin(
        SejOrder.__table__,
        SejOrder.order_no==LotEntry.entry_no,
    ).outerjoin(
        Order.__table__,
        and_(Order.id==LotEntry.order_id,
             Order.deleted_at==None)
    )



    def is_electing(self):
        return bool(self.lot_elect_work_id)

    def is_other_electing(self):
        return bool(self.lot_other_elect_work_id)

    def is_rejecting(self):
        return bool(self.lot_reject_work_id)

    @property
    def order_no(self):
        return self.entry_no

    @property
    def auth(self):
        class o(object):
            Status = self.Status
        return o

    @property
    def sej(self):
        class o(object):
            billing_number = self.sej_billing_number
            exchange_number = self.sej_exchange_number
        return o

    @property
    def sej_order(self):
        return self.sej

    @property
    def status(self):
        """ """
        if self.withdrawn_at:
            return u"ユーザ取消"
        if self.canceled_at:
            return u"キャンセル"
        if self.is_other_electing():
            return u"他の希望が当選予定"
        if self.closed_at:
            return u"終了"
        if self.elected_at:
            return u"当選"
        if self.is_electing():
            return u"当選予定"
        if self.is_rejecting():
            return u"落選予定"
        if self.rejected_at:
            return u"落選"
        return u"申込"

    @property
    def payment_method(self):
        class o(object):
            payment_plugin_id = self.payment_plugin_id
        return o

    @property
    def delivery_method(self):
        class o(object):
            delivery_plugin_id = self.delivery_plugin_id
        return o

    @property
    def shipping_address(self):
        if not self.shipping_address_id:
            return

        class o(object):
            last_name = self.shipping_address_last_name
            first_name = self.shipping_address_first_name
            last_name_kana = self.shipping_address_last_name_kana
            first_name_kana = self.shipping_address_first_name_kana
            prefecture = self.shipping_address_prefecture
            city = self.shipping_address_city
            address_1 = self.shipping_address_address_1
            address_2 = self.shipping_address_address_2
            tel_1 = self.shipping_address_tel_1
            tel_2 = self.shipping_address_tel_2
            email_1 = self.shipping_address_email_1
            email_2 = self.shipping_address_email_2
        return o

    products = orm.relationship('LotEntryProduct',
                                primaryjoin='and_(LotEntryWish.id==LotEntryProduct.lot_wish_id, LotEntryProduct.deleted_at==None)')

    @property
    def total_quantity(self):
        return sum([p.quantity for p in self.products])

class LotEntryReportSetting_ReportRecipient(Base):
    __tablename__   = 'LotEntryReportSetting_ReportRecipient'
    lot_entry_report_setting_id = Column(Identifier, ForeignKey('LotEntryReportSetting.id', ondelete='CASCADE'), primary_key=True)
    report_recipient_id = Column(Identifier, ForeignKey('ReportRecipient.id', ondelete='CASCADE'), primary_key=True)

class LotEntryReportSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = 'LotEntryReportSetting'
    query = DBSession.query_property()

    id = Column(Identifier, primary_key=True)

    event_id = Column(Identifier,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      nullable=True)
    event = orm.relationship('Event', backref='lot_entry_report_settings')
    lot_id = Column(Identifier,
                    ForeignKey('Lot.id', ondelete='CASCADE'),
                      nullable=True)
    lot = orm.relationship('Lot', backref='lot_entry_report_settings')

    frequency = Column(Integer, nullable=False)
    period = Column(Integer, nullable=False)
    time = Column(String(4), nullable=False)
    day_of_week = Column(Integer, nullable=True, default=None)
    start_on = Column(DateTime, nullable=True, default=None)
    end_on = Column(DateTime, nullable=True, default=None)
    recipients = orm.relationship('ReportRecipient', secondary=LotEntryReportSetting_ReportRecipient.__table__, backref='lot_entry_report_settings')

    def format_recipients(self):
        return u', '.join([r.format_recipient() for r in self.recipients])

    def format_emails(self):
        return u', '.join([r.email for r in self.recipients])

    @classmethod
    def in_term(cls, now):
        report_time = '{0:0>2}{1:0>2}'.format(now.hour, now.minute)[0:3] + '0'
        return and_(
            cls.time==report_time,
            or_(cls.start_on==None, cls.start_on<now),
            or_(cls.end_on==None, cls.end_on>now),
            or_(cls.day_of_week==None, cls.day_of_week==now.isoweekday())
        )

    @classmethod
    def query_in_term(cls, now):
        return cls.query.filter(cls.in_term(now))

    @classmethod
    def get_in_term(cls, now):
        return cls.query_in_term(now).all()

    @classmethod
    def query_reporting_about(cls, time, frequency, event_id=None, lot_id=None, day_of_week=None, id=None):
        query = cls.query
        query = query.filter(
            cls.frequency==frequency,
            cls.time==time,
        )

        if id:
            query = query.filter(cls.id!=id)
        if event_id:
            query = query.filter(cls.event_id==event_id)
        if lot_id:
            query = query.filter(cls.lot_id==lot_id)
        if frequency == ReportFrequencyEnum.Weekly.v[0]:
            query = query.filter(cls.day_of_week==day_of_week)
        return query


class CSVExporter(object):

    # specified for pymysql format param style; see PEP-249 DB API 2.0
    sql = u"""\
SELECT
    CASE
        WHEN LotEntryWish.withdrawn_at IS NOT NULL THEN 'ユーザ取消'
        WHEN LotEntry.closed_at IS NOT NULL THEN '終了'
        WHEN LotEntryWish.elected_at IS NOT NULL THEN '当選'
        WHEN LotEntryWish.rejected_at IS NOT NULL THEN '落選'
        WHEN LotEntryWish.canceled_at IS NOT NULL THEN 'キャンセル'
        WHEN LotElectWork.lot_entry_no IS NOT NULL THEN '当選予定'
        WHEN LotRejectWork.lot_entry_no IS NOT NULL THEN '落選予定'
        ELSE '申込'
    END AS `状態`,
    LotEntry.entry_no AS `申し込み番号`,
    LotEntryWish.wish_order + 1 AS `希望順序`,
    LotEntryWish.created_at AS `申し込み日`,
    -- NULL,
    p_sum.stock_names AS `席種`,
    p_sum.total_quantity AS `枚数`,
    Event.title AS `イベント`,
    Venue.name AS `会場`,
    Performance.name AS `公演`,
    Performance.code AS `公演コード`,
    Performance.start_on AS `公演日`,
    p_sum.names AS `商品`,
    PaymentMethod.name AS `決済方法`,
    DeliveryMethod.name AS `引取方法`,
    ShippingAddress.last_name AS `配送先姓`,
    ShippingAddress.first_name AS `配送先名`,
    ShippingAddress.last_name_kana AS `配送先姓(カナ)`,
    ShippingAddress.first_name_kana AS `配送先名(カナ)`,
    ShippingAddress.zip AS `郵便番号`,
    ShippingAddress.country AS `国`,
    ShippingAddress.prefecture AS `都道府県`,
    ShippingAddress.city AS `市区町村`,
    ShippingAddress.address_1 AS `住所1`,
    ShippingAddress.address_2 AS `住所2`,
    ShippingAddress.tel_1 AS `電話番号1`,
    ShippingAddress.tel_2 AS `電話番号2`,
    ShippingAddress.fax AS `FAX`,
    ShippingAddress.email_1 AS `メールアドレス1`,
    ShippingAddress.email_2 AS `メールアドレス2`,
    LotEntry.gender AS `性別`,
    LotEntry.birthday AS `誕生日`,
    LotEntry.memo AS `メモ`,
    UserProfile.last_name AS `姓`,
    UserProfile.first_name AS `名`,
    UserProfile.last_name_kana AS `姓(カナ)`,
    UserProfile.first_name_kana AS `名(カナ)`,
    UserProfile.nick_name AS `ニックネーム`,
    UserProfile.sex AS `プロフィールに設定されている性別`,
    UserProfile.birthday AS `プロフィールに設定されている誕生日`,
    LotEntry.channel AS `販売チャネル`,
    LotEntry.browserid AS `ブラウザID`,
    Membership.name AS `会員種別名`,
    MemberGroup.name AS `会員グループ名`,
    UserCredential.auth_identifier AS `会員種別ID`,
    LotEntryAttribute.name AS `attribute_name`,
    LotEntryAttribute.value AS `attribute_value`,
    NULL
FROM LotEntryWish
     JOIN LotEntry
     ON LotEntryWish.lot_entry_id = LotEntry.id AND LotEntry.deleted_at IS NULL
     JOIN Performance
     ON LotEntryWish.performance_id = Performance.id AND Performance.deleted_at IS NULL
     JOIN Venue
     ON Performance.id = Venue.performance_id AND Venue.deleted_at IS NULL
     JOIN Lot
     ON LotEntry.lot_id = Lot.id AND Lot.deleted_at IS NULL
     JOIN PaymentDeliveryMethodPair as PDMP
     ON LotEntry.payment_delivery_method_pair_id = PDMP.id AND PDMP.deleted_at IS NULL
     JOIN PaymentMethod
     ON PDMP.payment_method_id = PaymentMethod.id AND PaymentMethod.deleted_at IS NULL
     JOIN DeliveryMethod
     ON PDMP.delivery_method_id = DeliveryMethod.id  AND DeliveryMethod.deleted_at IS NULL
     JOIN Event
     ON Lot.event_id = Event.id AND Event.deleted_at IS NULL
     JOIN ShippingAddress
     ON LotEntry.shipping_address_id = ShippingAddress.id AND ShippingAddress.deleted_at IS NULL
     JOIN (
         SELECT
             LotEntryProduct.lot_wish_id,
             sum(LotEntryProduct.quantity) as total_quantity,
             group_concat(Product.name) as names,
             group_concat(StockType.name) as stock_names
         FROM LotEntryProduct
              JOIN LotEntryWish
              ON LotEntryProduct.lot_wish_id = LotEntryWish.id AND LotEntryWish.deleted_at IS NULL
              JOIN LotEntry
              ON LotEntryWish.lot_entry_id = LotEntry.id AND LotEntry.deleted_at IS NULL
              JOIN Product
              ON LotEntryProduct.product_id = Product.id AND Product.deleted_at IS NULL
              JOIN StockType
              ON Product.seat_stock_type_id = StockType.id AND StockType.deleted_at IS NULL
         WHERE LotEntry.lot_id = {}
         AND LotEntryProduct.deleted_at IS NULL
         GROUP BY LotEntryProduct.lot_wish_id
     ) p_sum
     ON p_sum.lot_wish_id = LotEntryWish.id
     LEFT JOIN User
     ON LotEntry.user_id = User.id AND User.deleted_at IS NULL
     LEFT JOIN UserProfile
     ON User.id = UserProfile.user_id AND UserProfile.deleted_at IS NULL
     LEFT JOIN LotElectWork
     ON LotElectWork.lot_id = Lot.id
     AND LotElectWork.lot_entry_no = LotEntry.entry_no
     AND LotElectWork.wish_order = LotEntryWish.wish_order
     LEFT JOIN LotRejectWork
     ON LotRejectWork.lot_id = Lot.id
     AND LotRejectWork.lot_entry_no = LotEntry.entry_no
     LEFT JOIN Membership
     ON LotEntry.membership_id=Membership.id AND Membership.deleted_at IS NULL
     LEFT JOIN MemberGroup
     ON LotEntry.membergroup_id=MemberGroup.id AND MemberGroup.deleted_at IS NULL
     LEFT JOIN UserCredential
     ON LotEntry.user_id=UserCredential.user_id AND LotEntry.membership_id=UserCredential.membership_id AND UserCredential.deleted_at IS NULL
     LEFT JOIN LotEntryAttribute
     ON LotEntryAttribute.lot_entry_id = LotEntry.id
WHERE Lot.id = {}
     AND LotEntryWish.deleted_at IS NULL
     AND {}
ORDER BY 申し込み番号, 希望順序, attribute_name

"""

    csv_columns = (
        u'状態',
        u'申し込み番号',
        u'希望順序',
        u'申し込み日',
        u'席種',
        u'枚数',
        u'イベント',
        u'会場',
        u'公演',
        u'公演コード',
        u'公演日',
        u'商品',
        u'決済方法',
        u'引取方法',
        u'配送先姓',
        u'配送先名',
        u'配送先姓(カナ)',
        u'配送先名(カナ)',
        u'郵便番号',
        u'国',
        u'都道府県',
        u'市区町村',
        u'住所1',
        u'住所2',
        u'電話番号1',
        u'電話番号2',
        u'FAX',
        u'メールアドレス1',
        u'メールアドレス2',
        u'性別',
        u'誕生日',
        u'メモ',
        u'姓',
        u'名',
        u'姓(カナ)',
        u'名(カナ)',
        u'ニックネーム',
        u'プロフィールに設定されている性別',
        u'プロフィールに設定されている誕生日',
        u'販売チャネル',
        u'ブラウザID',
        u'会員種別名',
        u'会員グループ名',
        u'会員種別ID',
    )

    def __init__(self, session, lot_id, condition=u'Lot.id IS NOT NULL'):
        self.session = session
        self.lot_id = lot_id
        self.condition = condition

    def __iter__(self):
        from sqlalchemy.dialects import mysql
        str_sql = self.sql.format(self.lot_id, self.lot_id, str(self.condition.compile(dialect=mysql.dialect())))
        cur = self.session.bind.execute(str_sql)
        try:
            prev_row = None
            row = None
            attribute_dict = OrderedDict()
            for row in cur.fetchall():
                if not prev_row:
                    prev_row = row

                self.update_attribute_dict(prev_row, attribute_dict)
                if prev_row[u'申し込み番号'] != row[u'申し込み番号'] or prev_row[u'希望順序'] != row[u'希望順序']:
                    order_dict = self.get_ordered_attribute_dict(prev_row, attribute_dict)
                    attribute_dict = OrderedDict()
                    yield order_dict
                prev_row = row

            self.update_attribute_dict(row, attribute_dict)
            yield self.get_ordered_attribute_dict(row, attribute_dict)
        finally:
            cur.close()

    @staticmethod
    def update_attribute_dict(prev_row, attribute_dict):
        if prev_row and prev_row[u'attribute_name']:
            attribute_dict[prev_row[u'attribute_name']] = prev_row[u'attribute_value']

    def get_ordered_dict(self, row):
        return OrderedDict([
            (c, row[c] if row[c] is not None else u'')
            for c in self.csv_columns]
        )

    def get_ordered_attribute_dict(self, row, attribute_dict):
        if not row:
            return None
        order_dict = self.get_ordered_dict(row)
        if attribute_dict:
            order_dict.update(attribute_dict)
        return order_dict

    def all(self):
        return list(self)
