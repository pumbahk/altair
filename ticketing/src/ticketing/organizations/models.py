# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ticketing.utils import StandardEnum
from ticketing.users.models import User
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted
from ticketing.master.models import Prefecture

class OrganizationTypeEnum(StandardEnum):
    Standard = 1

class Organization(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = "Organization"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    client_type = Column(Integer)
    city = Column(String(255))
    street = Column(String(255))
    address = Column(String(255))
    other_address = Column(String(255))
    tel_1 = Column(String(32))
    tel_2 = Column(String(32))
    fax = Column(String(32))

    user_id = Column(BigInteger, ForeignKey("User.id"), nullable=True)
    user = relationship("User", uselist=False)
    prefecture_id = Column(BigInteger, ForeignKey("Prefecture.id"), nullable=True)
    prefecture = relationship("Prefecture", uselist=False)

    venues = relationship("Venue", backref='organization')
    status = Column(Integer)
