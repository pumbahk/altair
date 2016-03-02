# encoding: utf-8

import logging
from enum import Enum
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import orm
from altair.saannotation import AnnotatedColumn
from pyramid.i18n import TranslationString as _
from altair.models import MutationDict, JSONEncodedDict, LogicallyDeleted, Identifier, WithTimestamp
from altair.app.ticketing.models import Base, BaseModel, DBSession, _flush_or_rollback
from altair.app.ticketing.orders.models import Order, Performance
from altair.app.ticketing.payments.plugins import FAMIPORT_PAYMENT_PLUGIN_ID, FAMIPORT_DELIVERY_PLUGIN_ID
from altair.app.ticketing.famiport.models import FamiPortSalesChannel, FamiPortPerformanceType
from altair.app.ticketing.core.models import SalesSegment
from sqlalchemy.orm.collections import attribute_mapped_collection

logger = logging.getLogger(__name__)

class AltairFamiPortReflectionStatus(Enum):
    Editing = 0
    AwaitingReflection = 1
    Reflected = 2


class AltairFamiPortVenue_Site(Base):
    __tablename__ = 'AltairFamiPortVenue_Site'
    __table_args__ = (
        sa.PrimaryKeyConstraint('altair_famiport_venue_id', 'site_id'),
        )

    altair_famiport_venue_id = AnnotatedColumn(Identifier, sa.ForeignKey('AltairFamiPortVenue.id', ondelete='CASCADE'), nullable=False)
    site_id = AnnotatedColumn(Identifier, sa.ForeignKey('Site.id', ondelete='CASCADE'), nullable=False)

class AltairFamiPortVenue_Venue(Base):
    __tablename__ = 'AltairFamiPortVenue_Venue'
    __table_args__ = (
        sa.PrimaryKeyConstraint('altair_famiport_venue_id', 'venue_id'),
        )

    altair_famiport_venue_id = AnnotatedColumn(Identifier, sa.ForeignKey('AltairFamiPortVenue.id', ondelete='CASCADE'), nullable=False)
    venue_id = AnnotatedColumn(Identifier, sa.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False)

class AltairFamiPortVenue(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortVenue'
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'famiport_venue_id'),
        )
   
    id = AnnotatedColumn(Identifier, primary_key=True, autoincrement=True)
    organization_id = AnnotatedColumn(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    siteprofile_id = AnnotatedColumn(Identifier, sa.ForeignKey('SiteProfile.id'), nullable=False)
    famiport_venue_id = AnnotatedColumn(Identifier, nullable=False)
    venue_name = AnnotatedColumn(sa.Unicode(50), nullable=False) # Venue.name
    name  = AnnotatedColumn(sa.Unicode(50), nullable=False) # Site.name
    name_kana = AnnotatedColumn(sa.Unicode(100), nullable=False)
    status = AnnotatedColumn(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = AnnotatedColumn(sa.DateTime(), nullable=True)

    organization = orm.relationship('Organization')
    siteprofile = orm.relationship('SiteProfile')
    sites = orm.relationship('Site', secondary=AltairFamiPortVenue_Site.__table__)
    venues = orm.relationship('Venue', secondary=AltairFamiPortVenue_Venue.__table__)


class AltairFamiPortPerformanceGroup(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortPerformanceGroup'

    id = AnnotatedColumn(Identifier, primary_key=True, autoincrement=True)
    organization_id = AnnotatedColumn(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    event_id = AnnotatedColumn(Identifier, sa.ForeignKey('Event.id'), nullable=False)
    code_1 = AnnotatedColumn(sa.Unicode(6), nullable=False, _a_label=u'興行コード')
    code_2 = AnnotatedColumn(sa.Unicode(4), nullable=False, _a_label=u'興行サブコード')
    name_1 = AnnotatedColumn(sa.Unicode(80), nullable=False, default=u'', _a_label=u'興行名称1')
    name_2 = AnnotatedColumn(sa.Unicode(80), nullable=False, default=u'', _a_label=u'興行名称2')
    sales_channel = AnnotatedColumn(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value, _a_label=u'販売種別')
    altair_famiport_venue_id = AnnotatedColumn(Identifier, sa.ForeignKey('AltairFamiPortVenue.id'), nullable=False)
    direct_sales_data = AnnotatedColumn(MutationDict.as_mutable(JSONEncodedDict(16384)))
    status = AnnotatedColumn(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value, _a_label=u'状態')
    last_reflected_at = AnnotatedColumn(sa.DateTime(), nullable=True, _a_label=u'最終反映日時')

    altair_famiport_venue = orm.relationship('AltairFamiPortVenue', backref='altair_famiport_performance_groups')
    event = orm.relationship('Event')
    organization = orm.relationship('Organization')

    altair_famiport_performances = orm.relationship('AltairFamiPortPerformance', collection_class=attribute_mapped_collection('performance'))

    @property
    def start_at(self):
        start_at = 0
        for altair_famiport_performance in self.altair_famiport_performances.values():
            _start_at = altair_famiport_performance.performance.start_on
            if start_at is 0 or _start_at is None or start_at > _start_at:
                start_at = _start_at
        if start_at is 0:
            start_at = None
        if start_at is None:
            start_at = datetime(1970, 1, 1, 0, 0, 0)
        return start_at

    @property
    def end_at(self):
        end_at_list = []
        for altair_famiport_performance in self.altair_famiport_performances.values():
            if altair_famiport_performance.performance.end_on is not None:
                end_at_list.append(altair_famiport_performance.performance.end_on)

        if len(end_at_list) == 0:
            end_at = datetime(2035, 12, 31, 23, 59, 59)
        else:
            end_at = max(end_at_list)
        return end_at

    @property
    def genre_1_code(self):
        return self.direct_sales_data and self.direct_sales_data.get('genre_1_code')

    @genre_1_code.setter
    def genre_1_code(self, value):
        if self.direct_sales_data is None:
            self.direct_sales_data = {}
        self.direct_sales_data['genre_1_code'] = value

    @property
    def genre_2_code(self):
        return self.direct_sales_data and self.direct_sales_data.get('genre_2_code')

    @genre_2_code.setter
    def genre_2_code(self, value):
        if self.direct_sales_data is None:
            self.direct_sales_data = {}
        self.direct_sales_data['genre_2_code'] = value

    @property
    def keywords(self):
        return self.direct_sales_data and self.direct_sales_data.get('keywords')

    @keywords.setter
    def keywords(self, value):
        if self.direct_sales_data is None:
            self.direct_sales_data = {}
        self.direct_sales_data['keywords'] = value

    @property
    def search_code(self):
        return self.direct_sales_data and self.direct_sales_data.get('search_code')

    @search_code.setter
    def search_code(self, value):
        if self.direct_sales_data is None:
            self.direct_sales_data = {}
        self.direct_sales_data['search_code'] = value


class AltairFamiPortPerformance(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortPerformance'
    __table_args__ = (
        sa.UniqueConstraint('performance_id'),
        )
    
    id = AnnotatedColumn(Identifier, primary_key=True, autoincrement=True)
    altair_famiport_performance_group_id = AnnotatedColumn(Identifier, sa.ForeignKey('AltairFamiPortPerformanceGroup.id', ondelete='CASCADE'), nullable=False)
    code = AnnotatedColumn(sa.Unicode(3), _a_label=u'公演コード')
    name = AnnotatedColumn(sa.Unicode(60), _a_label=u'公演名称')
    type = AnnotatedColumn(sa.Integer, nullable=False, default=FamiPortPerformanceType.Normal.value, _a_label=u'公演種別')
    performance_id = AnnotatedColumn(Identifier, sa.ForeignKey('Performance.id'), nullable=False)
    searchable = AnnotatedColumn(sa.Boolean, nullable=False, default=True, _a_label=u'公演情報開示フラグ')
    start_at = AnnotatedColumn(sa.DateTime(), nullable=True, _a_label=u'公演日時')
    ticket_name = AnnotatedColumn(sa.Unicode(20), nullable=True, _a_label=u'チケット名称')
    status = AnnotatedColumn(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = AnnotatedColumn(sa.DateTime(), nullable=True)

    performance = orm.relationship('Performance')
    altair_famiport_performance_group = orm.relationship('AltairFamiPortPerformanceGroup')

    def delete(self):
        # if self.reserved_orders():
        #      raise Exception(u'購入されている為、削除できません')
        # else:
        # Check FamiPortPerformance and FamiPortPerformanceGroup are not reflected
        if self.altair_famiport_performance_group.status != AltairFamiPortReflectionStatus.Reflected.value and self.status != AltairFamiPortReflectionStatus.Reflected.value:
            # Delete AltairFamiPortSalesSegmentPair
            for altair_famiport_sales_segment_pair in self.altair_famiport_sales_segment_pairs:
                altair_famiport_sales_segment_pair.delete()
            # Delete AltairFamiPortPerformance
            self.deleted_at = datetime.now()
            DBSession.merge(self)
            _flush_or_rollback()
        else:
            raise Exception(u'ステータスが反映済みのため、削除できません')


class AltairFamiPortSalesSegmentPair(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortSalesSegmentPair'

    id = AnnotatedColumn(Identifier, primary_key=True, autoincrement=True)
    altair_famiport_performance_id = AnnotatedColumn(Identifier, sa.ForeignKey('AltairFamiPortPerformance.id'), nullable=False)
    code = AnnotatedColumn(sa.Unicode(3), nullable=False)
    name = AnnotatedColumn(sa.Unicode(40), nullable=False)
    seat_unselectable_sales_segment_id = AnnotatedColumn(Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True)
    seat_selectable_sales_segment_id = AnnotatedColumn(Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True)
    published_at = AnnotatedColumn(sa.DateTime(), nullable=True)
    auth_required = AnnotatedColumn(sa.Boolean, nullable=False, default=False)
    auth_message = AnnotatedColumn(sa.Unicode(320), nullable=False, default=u'')
    status = AnnotatedColumn(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = AnnotatedColumn(sa.DateTime(), nullable=True)

    altair_famiport_performance = orm.relationship('AltairFamiPortPerformance', backref='altair_famiport_sales_segment_pairs')
    seat_unselectable_sales_segment = orm.relationship('SalesSegment', primaryjoin=(seat_unselectable_sales_segment_id==SalesSegment.id), foreign_keys=[seat_unselectable_sales_segment_id])
    seat_selectable_sales_segment = orm.relationship('SalesSegment', primaryjoin=(seat_selectable_sales_segment_id==SalesSegment.id), foreign_keys=[seat_selectable_sales_segment_id])

    def validate(self):
        errors = []
        if self.seat_unselectable_sales_segment is not None and self.seat_unselectable_sales_segment.public:
            if self.seat_selectable_sales_segment is not None and self.seat_selectable_sales_segment.public:
                if self.seat_unselectable_sales_segment is not None:
                    if self.seat_unselectable_sales_segment.end_at + timedelta(seconds=1) != self.seat_selectable_sales_segment.start_at:
                        errors.append(u'there is a gap between the sales term of the seat-unselectable sales segment and the seat-selectable sales segment; they should be adjacent')
        else:
            if self.seat_selectable_sales_segment is None or not self.seat_selectable_sales_segment.public:
                errors.append(u'neither seat-unselectable or seat-selectable sales segment is specified or public')
        return errors

    def delete(self):
        # Check AltairFamiPortSalesSegmentPair is not reflected
        if self.status != AltairFamiPortReflectionStatus.Reflected.value:
            self.deleted_at = datetime.now()
            DBSession.merge(self)
            _flush_or_rollback()
        else:
            raise Exception(u'ステータスが反映済みのため、削除できません')

    @property
    def seat_selection_start_at(self):
        assert len(self.validate()) == 0
        if self.seat_selectable_sales_segment is not None and self.seat_selectable_sales_segment.public:
            return self.seat_selectable_sales_segment.start_at
        else:
            return None

    @property
    def start_at(self):
        assert len(self.validate()) == 0
        if self.seat_unselectable_sales_segment is not None and self.seat_unselectable_sales_segment.public:
            return self.seat_unselectable_sales_segment.start_at
        elif self.seat_selectable_sales_segment is not None and self.seat_selectable_sales_segment.public:
            return self.seat_selectable_sales_segment.start_at
        return None

    @property
    def end_at(self):
        assert len(self.validate()) == 0
        if self.seat_selectable_sales_segment is not None and self.seat_selectable_sales_segment.public:
            return self.seat_selectable_sales_segment.end_at
        elif self.seat_unselectable_sales_segment is not None and self.seat_unselectable_sales_segment.public:
            return self.seat_unselectable_sales_segment.end_at
        return None


class AltairFamiPortNotificationType(Enum):
    PaymentCompleted = 1
    TicketingCompleted = 2
    PaymentAndTicketingCompleted = 3
    PaymentCanceled  = 4
    TicketingCanceled  = 8
    PaymentAndTicketingCanceled = 12
    OrderCanceled = 16
    Refunded  = 32
    OrderExpired = 64


class AltairFamiPortNotification(Base, WithTimestamp):
    __tablename__ = 'AltairFamiPortNotification'

    id = AnnotatedColumn(Identifier, primary_key=True, autoincrement=True)
    type = AnnotatedColumn(sa.Integer, nullable=False)
    client_code = AnnotatedColumn(sa.Unicode(24), nullable=False)
    order_no = AnnotatedColumn(sa.Unicode(12), nullable=False)
    famiport_order_identifier = AnnotatedColumn(sa.Unicode(12), nullable=False)
    payment_reserve_number = AnnotatedColumn(sa.Unicode(13), nullable=True)
    ticketing_reserve_number = AnnotatedColumn(sa.Unicode(13), nullable=True)

    reflected_at = AnnotatedColumn(sa.DateTime(), nullable=True, index=True)
