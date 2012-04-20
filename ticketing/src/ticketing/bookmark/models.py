# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, column_property, mapper

from ticketing.clients.models import Client
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class Bookmark(Base):
    __tablename__ = "Bookmark"
    id              = Column(BigInteger, primary_key=True)
    name            = Column(String(255))
    url             = Column(String(1024))
    client_id       = Column(BigInteger, ForeignKey("Client.id"), nullable=True)
    client          = relationship("Client", uselist=False)
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)