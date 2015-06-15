from enum import Enum
from datetime import datetime, timedelta
import sqlalchemy as sa
from sqlalchemy import orm
from altair.models import MutationDict, JSONEncodedDict, LogicallyDeleted, Identifier, WithTimestamp
from altair.app.ticketing.models import Base, BaseModel
from altair.app.ticketing.famiport.models import FamiPortSalesChannel, FamiPortPerformanceType
from altair.app.ticketing.core.models import SalesSegment
from sqlalchemy.orm.collections import attribute_mapped_collection

class AltairFamiPortReflectionStatus(Enum):
    Editing = 0
    AwaitingReflection = 1
    Reflected = 2

class AltairFamiPortVenue(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortVenue'
    __table_args__ = (
        sa.UniqueConstraint('organization_id', 'site_id', 'famiport_venue_id'),
        )
   
    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    site_id = sa.Column(Identifier, sa.ForeignKey('Site.id'), nullable=False)
    famiport_venue_id = sa.Column(Identifier, nullable=False)
    name  = sa.Column(sa.Unicode(50), nullable=False)
    name_kana = sa.Column(sa.Unicode(100), nullable=False)
    status = sa.Column(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = sa.Column(sa.DateTime(), nullable=True)

    organization = orm.relationship('Organization')
    site = orm.relationship('Site')

class AltairFamiPortPerformanceGroup(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortPerformanceGroup'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    organization_id = sa.Column(Identifier, sa.ForeignKey('Organization.id'), nullable=False)
    event_id = sa.Column(Identifier, sa.ForeignKey('Event.id'), nullable=False)
    code_1 = sa.Column(sa.Unicode(6), nullable=False)
    code_2 = sa.Column(sa.Unicode(4), nullable=False)
    name_1 = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    name_2 = sa.Column(sa.Unicode(80), nullable=False, default=u'')
    sales_channel = sa.Column(sa.Integer, nullable=False, default=FamiPortSalesChannel.FamiPortOnly.value)
    altair_famiport_venue_id = sa.Column(Identifier, sa.ForeignKey('AltairFamiPortVenue.id'), nullable=False)
    direct_sales_data = sa.Column(MutationDict.as_mutable(JSONEncodedDict(16384)))
    status = sa.Column(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = sa.Column(sa.DateTime(), nullable=True)

    altair_famiport_venue = orm.relationship('AltairFamiPortVenue', backref='altair_famiport_performance_groups')
    event = orm.relationship('Event')
    organization = orm.relationship('Organization')

    altair_famiport_performances = orm.relationship('AltairFamiPortPerformance', collection_class=attribute_mapped_collection('performance'))

    @property
    def start_at(self):
        start_at = 0
        for altair_famiport_performance in self.altair_famiport_performances:
            _start_at = altair_famiport_performance.performance.start_at
            if start_at is 0 or _start_at is None or start_at > _start_at:
                start_at = _start_at
        if start_at is 0:
            start_at = None
        if start_at is None:
            start_at = datetime(1970, 1, 1, 0, 0, 0)
        return start_at

    @property
    def end_at(self):
        end_at = 0
        for altair_famiport_performance in self.altair_famiport_performances:
            _end_at = altair_famiport_performance.performance.end_at
            if end_at is 0 or _end_at is None or end_at > _end_at:
                end_at = _end_at
        if end_at is 0:
            end_at = None
        if end_at is None:
            end_at = datetime(2035, 12, 31, 23, 59, 59)
        return end_at


class AltairFamiPortPerformance(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortPerformance'
    __table_args__ = (
        sa.UniqueConstraint('performance_id'),
        )
    
    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    altair_famiport_performance_group_id = sa.Column(Identifier, sa.ForeignKey('AltairFamiPortPerformanceGroup.id', ondelete='CASCADE'), nullable=False)
    code = sa.Column(sa.Unicode(3))
    name = sa.Column(sa.Unicode(60))
    type = sa.Column(sa.Integer, nullable=False, default=FamiPortPerformanceType.Normal.value)
    performance_id = sa.Column(Identifier, sa.ForeignKey('Performance.id'), nullable=False)
    searchable = sa.Column(sa.Boolean, nullable=False, default=True)
    start_at = sa.Column(sa.DateTime(), nullable=True)
    ticket_name = sa.Column(sa.Unicode(20), nullable=True)
    status = sa.Column(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = sa.Column(sa.DateTime(), nullable=True)

    performance = orm.relationship('Performance')
    altair_famiport_performance_group = orm.relationship('AltairFamiPortPerformanceGroup')


class AltairFamiPortSalesSegmentPair(Base, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'AltairFamiPortSalesSegmentPair'

    id = sa.Column(Identifier, primary_key=True, autoincrement=True)
    altair_famiport_performance_id = sa.Column(Identifier, sa.ForeignKey('AltairFamiPortPerformance.id'), nullable=False)
    code = sa.Column(sa.Unicode(3), nullable=False)
    name = sa.Column(sa.Unicode(40), nullable=False)
    seat_unselectable_sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True)
    seat_selectable_sales_segment_id = sa.Column(Identifier, sa.ForeignKey('SalesSegment.id'), nullable=True)
    published_at = sa.Column(sa.DateTime(), nullable=True)
    auth_required = sa.Column(sa.Boolean, nullable=False, default=False)
    auth_message = sa.Column(sa.Unicode(320), nullable=False, default=u'')
    status = sa.Column(sa.Integer(), default=AltairFamiPortReflectionStatus.Editing.value)
    last_reflected_at = sa.Column(sa.DateTime(), nullable=True)

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
