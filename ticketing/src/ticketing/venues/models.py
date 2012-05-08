from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property, mapper

import sqlahelper

from ticketing.utils import StandardEnum
from ticketing.models import BaseModel, JSONEncodedDict, MutationDict

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

seat_venue_area_table = Table(
    'Seat_VenueArea', Base.metadata,
    Column('venue_area_id', BigInteger, ForeignKey('VenueArea.id'), primary_key=True),
    Column('seat_id', BigInteger, ForeignKey('Seat.id'), primary_key=True)
)

class Site(Base):
    __tablename__ = "Site"
    id = Column(BigInteger, primary_key=True)
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

class Venue(Base):
    __tablename__ = "Venue"
    id = Column(BigInteger, primary_key=True)
    site_id = Column(BigInteger, ForeignKey("Site.id"), nullable=True)
    name = Column(String(255))
    sub_name = Column(String(255))
    organization_id = Column(BigInteger, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization')

    site = relationship("Site")
    seats = relationship("Seat", backref='venue')
    areas = relationship("VenueArea", backref='venue')
    performances = relationship("Performance", backref='venue')

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    @staticmethod
    def get(id):
        return session.query(Venue).filter(Venue.id==id).first()

    @staticmethod
    def get_by_organization_id(id):
        return session.query(Venue).filter(Venue.organization_id==id).all()

    @staticmethod
    def all():
        return session.query(Venue).all()

class VenueArea(Base):
    __tablename__   = "VenueArea"
    id              = Column(BigInteger, primary_key=True)
    name            = Column(String(255))

    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))

    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

class SeatAttribute(Base):
    __tablename__   = "SeatAttribute"
    seat_id         = Column(BigInteger, ForeignKey('Seat.id'), primary_key=True, nullable=False)
    name            = Column(String(255), primary_key=True, nullable=False)
    value           = Column(String(1023))

class Seat(Base):
    __tablename__   = "Seat"
    id              = Column(BigInteger, primary_key=True)
    l0_id           = Column(String(255))

    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    stock_id        = Column(BigInteger, ForeignKey('Stock.id'))

    attributes      = relationship("SeatAttribute", backref='seat', cascade='save-update, merge')

    areas           = relationship("VenueArea", secondary=seat_venue_area_table, backref="seats")

    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)

    def __setitem__(self, name, value):
        session.add(self)
        session.flush([self])
        session.merge(SeatAttribute(seat_id=self.id, name=name, value=value))

    def __getitem__(self, name):
        attr = session.query(SeatAttribute).get((self.id, name))
        if attr is None:
            raise KeyError(name)
        return attr.value

    # @TODO
    @staticmethod
    def get_grouping_seat_sets(pid, stid):
        return [[]]

class SeatStatusEnum(StandardEnum):
    Vacant = 1
    InCart = 2
    Ordered = 3
    Confirmed = 4
    Shipped = 5
    Canceled = 6
    Reserved = 7

# stock based on phisical seat positions
class SeatStatus(BaseModel, Base):
    __tablename__ = "SeatStatus"
    seat_id = Column(BigInteger, ForeignKey("Seat.id"), primary_key=True)
    status = Column(Integer)

    seat = relationship('Seat', uselist=False, backref="status") # 1:1

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



