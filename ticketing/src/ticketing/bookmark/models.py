# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import join, column_property, mapper

from ticketing.core.models import Organization
from hashlib import md5

import sqlahelper

from ticketing.models import WithTimestamp, Identifier, relationship

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class Bookmark(Base, WithTimestamp):
    __tablename__ = "Bookmark"

    id              = Column(Identifier, primary_key=True)
    name            = Column(String(255))
    url             = Column(String(1024))
    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization    = relationship("Organization", uselist=False)
    status          = Column(Integer)

    @staticmethod
    def get(bookmark_id):
        return session.query(Bookmark).filter(Bookmark.id==bookmark_id).first()

    @staticmethod
    def find_by_organization_id(organization_id):
        return session.query(Bookmark).filter(Bookmark.organization_id==organization_id).all()
