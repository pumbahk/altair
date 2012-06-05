# encoding: utf-8
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, ForeignKeyConstraint, Index, DECIMAL
from sqlalchemy.orm import join, backref, column_property, mapper
from sqlalchemy.ext.associationproxy import association_proxy

import sqlahelper

from ticketing.utils import StandardEnum
from ticketing.models import BaseModel, JSONEncodedDict, MutationDict, WithTimestamp, LogicallyDeleted, Identifier, DBSession, relationship

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

seat_seat_adjacency_table = Table(
    "Seat_SeatAdjacency", Base.metadata,
    Column('seat_id', Identifier, ForeignKey("Seat.id"), primary_key=True, nullable=False),
    Column('seat_adjacency_id', Identifier, ForeignKey("SeatAdjacency.id"), primary_key=True, nullable=False)
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
    venue_id = Column(Identifier, ForeignKey('Venue.id'), primary_key=True, nullable=False)
    group_l0_id = Column(String(255), primary_key=True, nullable=False)
    venue_area_id = Column(Identifier, ForeignKey('VenueArea.id'), index=True, primary_key=True, nullable=False)
    venue = relationship('Venue')

class Venue(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Venueは、Performance毎に1個つくられる。
    Venueのテンプレートは、performance_idがNoneになっている。
    """
    __tablename__ = "Venue"
    id = Column(Identifier, primary_key=True)
    site_id = Column(Identifier, ForeignKey("Site.id"), nullable=False)
    performance_id = Column(Identifier, ForeignKey("Performance.id"), nullable=True)
    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=False)
    name = Column(String(255))
    sub_name = Column(String(255))

    original_venue_id = Column(Identifier, ForeignKey("Venue.id"), nullable=True)
    derived_venues = relationship("Venue",
                                  backref=backref(
                                    'original_venue', remote_side=[id]))
                                  
    adjacency_sets = relationship("SeatAdjacencySet", backref='venue')

    site = relationship("Site", uselist=False)
    seats = relationship("Seat", backref='venue')
    areas = relationship("VenueArea", backref='venues', secondary=VenueArea_group_l0_id.__table__)
    organization = relationship("Organization", backref='venues')

    @staticmethod
    def create_from_template(template, performance_id):
        venue = Venue.clone(template)
        venue.original_venue_id = template.id
        venue.performance_id = performance_id
        venue.save()

        for template_area in template.areas:
            VenueArea.create_from_template(template=template_area, venue_id=venue.id)

        for template_seat in template.seats:
            Seat.create_from_template(template=template_seat, venue_id=venue.id)

    def delete_cascade(self):
        self.delete()

        for area in self.areas:
            area.delete_cascade()

        for seat in self.seats:
            seat.delete_cascade()

class VenueArea(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "VenueArea"
    id              = Column(Identifier, primary_key=True)
    name            = Column(String(255), nullable=False)
    groups          = relationship('VenueArea_group_l0_id')

    @staticmethod
    def create_from_template(template, venue_id):
        area = VenueArea.clone(template)
        area.venue_id = venue_id
        area.save()

        for template_group in template.groups:
            group = VenueArea_group_l0_id(
                group_l0_id=template_group.group_l0_id,
                venue_id=venue_id,
                venue_area_id=area.id
            )
            DBSession.add(group)

    def delete_cascade(self):
        self.delete()

        for group in self.groups:
            DBSession.delete(group)

class SeatAttribute(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "SeatAttribute"
    seat_id         = Column(Identifier, ForeignKey('Seat.id'), primary_key=True, nullable=False)
    name            = Column(String(255), primary_key=True, nullable=False)
    value           = Column(String(1023))

    @staticmethod
    def create_from_template(template, seat_id):
        attribute = SeatAttribute.clone(template)
        attribute.seat_id = seat_id
        attribute.save()

class Seat(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__   = "Seat"
    __table_args__  = (
        ForeignKeyConstraint(
            ['venue_id', 'group_l0_id'],
            [VenueArea_group_l0_id.venue_id, VenueArea_group_l0_id.group_l0_id]
            ),
        )

    id              = Column(Identifier, primary_key=True)
    l0_id           = Column(String(255))

    stock_id        = Column(Identifier, ForeignKey('Stock.id'))
    stock_type_id   = Column(Identifier, ForeignKey('StockType.id'))

    venue_id        = Column(Identifier, ForeignKey('Venue.id'), nullable=False)
    group_l0_id     = Column(String(255))

    attributes      = relationship("SeatAttribute", backref='seat', cascade='save-update, merge')
    areas           = relationship("VenueArea", secondary=VenueArea_group_l0_id.__table__, backref="seats")
    adjacencies     = relationship("SeatAdjacency", secondary=seat_seat_adjacency_table, backref="seats")
    _status = relationship('SeatStatus', uselist=False, backref='seat') # 1:1

    status = association_proxy('_status', 'status')

    def __setitem__(self, name, value):
        session.add(self)
        session.flush([self])
        session.merge(SeatAttribute(seat_id=self.id, name=name, value=value))

    def __getitem__(self, name):
        attr = session.query(SeatAttribute).get((self.id, name))
        if attr is None:
            raise KeyError(name)
        return attr.value

    @staticmethod
    def create_from_template(template, venue_id):
        seat = Seat.clone(template)
        seat.venue_id = venue_id
        seat.stock_id = None
        if not seat.stock_type_id:
            seat.stock_type_id = None
        seat.save()

        for template_attribute in template.attributes:
            SeatAttribute.create_from_template(template=template_attribute, seat_id=seat.id)

    def delete_cascade(self):
        self.delete()

        for attribute in self.attributes:
            attribute.delete()

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
    seat_id = Column(Identifier, ForeignKey("Seat.id"), primary_key=True)
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

class SeatAdjacency(Base):
    __tablename__ = "SeatAdjacency"
    id = Column(Identifier, primary_key=True)
    adjacency_set_id = Column(Identifier, ForeignKey('SeatAdjacencySet.id'))

class SeatAdjacencySet(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "SeatAdjacencySet"
    id = Column(Identifier, primary_key=True)
    venue_id = Column(Identifier, ForeignKey('Venue.id'))
    seat_count = Column(Integer, nullable=False)
    adjacencies = relationship("SeatAdjacency", backref='adjacency_set')

