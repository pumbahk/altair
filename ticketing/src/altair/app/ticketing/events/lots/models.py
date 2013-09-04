# -*- coding:utf-8 -*-

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
    Order,
    ShippingAddress,
)
from altair.app.ticketing.core.models import (
    ReportFrequencyEnum,
    #ReportPeriodEnum,
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
            LotEntryWish.__table__.c.id,
            LotEntryWish.__table__.c.created_at,
            LotEntry.__table__.c.entry_no,
            LotEntry.__table__.c.closed_at,
            LotEntry.__table__.c.ordered_mail_sent_at,
            LotEntryWish.__table__.c.wish_order,
            LotEntryWish.__table__.c.canceled_at,
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
        SejOrder.order_id==LotEntry.entry_no,
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
    def status(self):
        """ """
        if self.is_other_electing():
            return u"他の希望が当選予定"
        if self.closed_at:
            return u"終了"
        if self.elected_at:
            return u"当選"
        if self.is_electing():
            return u"当選予定"
        if self.canceled_at:
            return u"キャンセル"
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

    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), nullable=True)
    operator = orm.relationship('Operator', backref='lot_entry_report_setting')

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

    @classmethod
    def in_term(cls, now):
        return and_(
            cls.time==now.hour,
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
    def query_reporting_about(cls, time, frequency, 
                              event_id=None, lot_id=None,
                              day_of_week=None):
        query = cls.query
        query = query.filter(
            cls.frequency==frequency,
            cls.time==time,
        )

        if event_id:
            query = query.filter(cls.event_id==event_id)
        if lot_id:
            query = query.filter(cls.lot_id==lot_id)
        if frequency == ReportFrequencyEnum.Weekly.v[0]:
            query = query.filter(cls.day_of_week==day_of_week)
        return query

