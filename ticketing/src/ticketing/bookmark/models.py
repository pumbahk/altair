# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, join, column_property, mapper

from ticketing.organizations.models import Organization
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class Bookmark(Base):
    __tablename__ = "Bookmark"

    id              = Column(BigInteger, primary_key=True)
    name            = Column(String(255))
    url             = Column(String(1024))
    client_id       = Column(BigInteger, ForeignKey("Organization.id"), nullable=True)
    client          = relationship("Organization", uselist=False)
    updated_at      = Column(DateTime)
    created_at      = Column(DateTime)
    status          = Column(Integer)

    @staticmethod
    def get(bookmark_id):
        return session.query(Bookmark).filter(Bookmark.id==bookmark_id).first()

    @staticmethod
    def find_by_client_id(client_id):
        return session.query(Bookmark).filter(Bookmark.client_id==client_id).all()