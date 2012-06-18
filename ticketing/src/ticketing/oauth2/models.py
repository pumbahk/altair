#-*- coding: utf-8 -*-

"""OAuth 2.0 Django Models"""

import time

from hashlib import sha512
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL

from ticketing.oauth2.consts import CLIENT_KEY_LENGTH, CLIENT_SECRET_LENGTH,\
                                    ACCESS_TOKEN_LENGTH, REFRESH_TOKEN_LENGTH,\
                                    ACCESS_TOKEN_EXPIRATION, MAC_KEY_LENGTH, REFRESHABLE,\
                                    CODE_KEY_LENGTH, CODE_EXPIRATION

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.models import BaseModel
from ticketing.operators.models import Operator
from ticketing.models import WithTimestamp, Identifier, relationship

class TimestampGenerator(object):
    """Callable Timestamp Generator that returns a UNIX time integer.

    **Kwargs:**

    * *seconds:* A integer indicating how many seconds in the future the
      timestamp should be. *Default 0*

    *Returns int*
    """
    def __init__(self, seconds=0):
        self.seconds = seconds

    def __call__(self):
        return datetime.fromtimestamp(int(time.time()) + self.seconds)


class KeyGenerator(object):
    """Callable Key Generator that returns a random keystring.

    **Args:**

    * *length:* A integer indicating how long the key should be.

    *Returns str*
    """
    def __init__(self, length):
        self.length = length

    def __call__(self):
        return sha512(uuid4().hex).hexdigest()[0:self.length]

class Service(Base, BaseModel, WithTimestamp):
    __tablename__ = 'Service'
    id              = Column(Identifier, primary_key=True)
    name            = Column(String(255))
    key             = Column(String(CLIENT_KEY_LENGTH), default=KeyGenerator(CLIENT_KEY_LENGTH), index=True, unique=True)
    secret          = Column(String(CLIENT_SECRET_LENGTH), default=KeyGenerator(CLIENT_SECRET_LENGTH),unique=True)
    redirect_uri    = Column(String(1024))
    status          = Column(Integer)

    @staticmethod
    def get_key(key):
        return session.query(Service).filter(Service.key == key).first()


class AccessToken(Base, BaseModel, WithTimestamp):
    __tablename__ = 'AccessToken'
    id          = Column(Identifier, primary_key=True)

    service = relationship("Service")
    service_id = Column(Identifier, ForeignKey("Service.id"))
    operator = relationship("Operator")
    operator_id = Column(Identifier, ForeignKey("Operator.id"))

    key             = Column(String(CODE_KEY_LENGTH), default=KeyGenerator(CODE_KEY_LENGTH), index=True, unique=True)
    token           = Column(String(ACCESS_TOKEN_LENGTH), default=KeyGenerator(ACCESS_TOKEN_LENGTH), index=True, unique=True)
    refresh_token   = Column(String(REFRESH_TOKEN_LENGTH), default=KeyGenerator(REFRESH_TOKEN_LENGTH), index=True, unique=True, nullable=True)
    mac_key         = Column(String(MAC_KEY_LENGTH), index=True, unique=True, nullable=True)

    issue = Column(Integer, default=TimestampGenerator())
    expire = Column(DateTime, default=TimestampGenerator(ACCESS_TOKEN_EXPIRATION))
    refreshable = Column(Boolean, default=REFRESHABLE)
    status = Column(Integer, default=1)

    @staticmethod
    def get(id):
        return session.query(AccessToken).filter(AccessToken.id == id).first()

    @staticmethod
    def get_by_key(key):
        return session.query(AccessToken).filter(AccessToken.key == key).first()


class MACNonce(Base, BaseModel, WithTimestamp):
    __tablename__       = 'MACNonce'
    id                  = Column(Identifier, primary_key=True)
    access_token        = relationship("AccessToken")
    access_token_id     = Column(Identifier, ForeignKey("AccessToken.id"))
    nonce               = Column(String(30), index=True)

    status              = Column(Integer, default=1)

