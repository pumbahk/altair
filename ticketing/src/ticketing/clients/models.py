# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ticketing.utils import StandardEnum

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.master.models import Prefecture

class ClientTypeEnum(StandardEnum):
    Standard        = 1

class Client(Base):
    __tablename__ = "Client"
    id          = Column(BigInteger, primary_key=True)
    name        = Column(String(255))
    client_type = Column(Integer)
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

    @staticmethod
    def get(client_id):
        return session.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def update(client):
        session.merge(client)
        session.flush()

    @staticmethod
    def all():
        return session.query(Client).all()

