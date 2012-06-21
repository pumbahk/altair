# -*- coding:utf-8 -*-

# -*- coding: utf-8 -*-

from ticketing.models import BaseModel, LogicallyDeleted, WithTimestamp, MutationDict, JSONEncodedDict, relationship, Identifier
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, Date, ForeignKey, Enum, DECIMAL, Binary
from sqlalchemy.orm import relationship, join, column_property, mapper, backref

from datetime import datetime
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class Uranai_User(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'ticketstar_playguide.User'
    id                      = Column(Identifier, primary_key=True)
    canMail                 = Column(String(255))
    canMobileMail           = Column(String(255))
    email                   = Column(String(255))
    mobileEmail             = Column(String(255))
    nameKana                = Column(String(255))
    openidKey               = Column(String(255))

class Uranai_Order(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'ticketstar_playguide.Order'
    id                      = Column(Identifier, primary_key=True)


