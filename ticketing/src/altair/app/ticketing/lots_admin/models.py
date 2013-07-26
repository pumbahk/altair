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
from sqlalchemy.orm import (
    relationship,
)

from altair.models import (
    Identifier,
    WithTimestamp,
)

from altair.app.ticketing.models import (
    Base,
    DBSession,
    BaseModel,
    LogicallyDeleted,
)

from altair.app.ticketing.core.models import (
    Event,
    #Performance,
    ShippingAddress,
    ReportFrequencyEnum,
    ReportPeriodEnum,
)

from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
)

class LotEntrySearch(Base):
    __table__ = LotEntry.__table__.join(
        Lot.__table__,
        Lot.id==LotEntry.lot_id
        ).join(
        Event.__table__,
        Event.id==Lot.event_id
        ).join(
        ShippingAddress.__table__,
        ShippingAddress.id==LotEntry.shipping_address_id)

    __mapper_args__ = dict(
        include_properties=[
            LotEntry.__table__.c.id,
            LotEntry.__table__.c.entry_no,
            Lot.__table__.c.id.label('lot_id'),
            Lot.__table__.c.name.label('lot_name'),
            Event.__table__.c.organization_id,
            Event.__table__.c.title,
            Event.__table__.c.id.label('event_id'),
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
            LotEntry.__table__.c.created_at,
            ],
        primary_key=[
            LotEntry.__table__.c.id,
            ]
        )

    id = LotEntry.__table__.c.id
    entry_no = LotEntry.__table__.c.entry_no
    lot_id = Lot.__table__.c.id
    lot_name = Lot.__table__.c.name
    organization_id = Event.__table__.c.organization_id
    event_id = Event.__table__.c.id
    event_title = Event.__table__.c.title
    shipping_address_id = ShippingAddress.__table__.c.id
    shipping_address_full_name = ShippingAddress.__table__.c.last_name + u'　' + ShippingAddress.__table__.c.first_name
    shipping_address_full_name_kana = ShippingAddress.__table__.c.last_name_kana + u'　' + ShippingAddress.__table__.c.first_name_kana
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
    created_at = LotEntry.__table__.c.created_at

    def __repr__(self):
        return ("<{0.__class__.__name__} "
                "organization_id={0.organization_id} "
                "entry_no={0.entry_no}>".format(self))

class LotEntryReportSetting(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = 'LotEntryReportSetting'
    query = DBSession.query_property()

    id = Column(Identifier, primary_key=True)

    event_id = Column(Identifier, 
                      ForeignKey('Event.id', ondelete='CASCADE'), 
                      nullable=True)
    event = relationship('Event', backref='lot_entry_report_settings')
    lot_id = Column(Identifier, 
                    ForeignKey('Lot.id', ondelete='CASCADE'), 
                      nullable=True)
    lot = relationship('Lot', backref='lot_entry_report_settings')

    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), nullable=True)
    operator = relationship('Operator', backref='lot_entry_report_setting')

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
