from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property, mapper

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

venue_venue_area_table = Table(
    'Venue_SeatMasterVenueArea', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('venue_area_id', BigInteger, ForeignKey('VenueArea.id')),
    Column('seat_master_id', BigInteger, ForeignKey('SeatMaster.id'))
)

class SeatType(Base):
    __tablename__ = 'SeatType'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    event_id = Column(BigInteger, ForeignKey('Event.id'))
    event = relationship('Event', uselist=False)
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class Venue(Base):
    __tablename__ = "Venue"
    id = Column(BigInteger, primary_key=True)

    name = Column(String(255))
    sub_name = Column(String(255))

    zip = Column(String(255))
    prefecture_id = Column(BigInteger, ForeignKey("Prefecture.id"), nullable=True)
    prefecture    = relationship("Prefecture", uselist=False)
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

class VenueArea(Base):
    __tablename__ = "VenueArea"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

# Layer1 SeatMaster
class SeatMaster(Base):
    __tablename__ = "SeatMaster"
    id              = Column(BigInteger, primary_key=True)
    identifieir     = Column(String(255))
    venue           = relationship('Venue')
    venue_id        = Column(BigInteger, ForeignKey('Venue.id'))
    areas           = relationship("VenueArea",
                        secondary=venue_venue_area_table, backref="seats")
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

# Layer2 SeatMaster
class SeatMasterL2(Base):
    __tablename__ = "SeatMasterL2"
    id = Column(BigInteger, primary_key=True)
    performance_id = Column(BigInteger, ForeignKey('Performance.id'))
    performance = relationship('Performance', uselist=False)
    seat_type_id = Column(BigInteger, ForeignKey('SeatType.id'))
    seat_type = relationship('SeatType', uselist=False)
    seat_id = Column(BigInteger, ForeignKey('SeatMaster.id'))
    seat = relationship('SeatMaster', uselist=False)
    # @TODO have some attributes regarding Layer2
    #venue_id = Column(BigInteger)

    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)

    # @TODO
    @staticmethod
    def get_grouping_seat_sets(pid, stid):
        return [[]]
