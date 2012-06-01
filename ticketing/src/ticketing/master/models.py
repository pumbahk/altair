from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import join, backref, column_property

import sqlahelper

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, relationship

'''
 Master Data
'''
class Prefecture(Base, BaseModel):
    __tablename__ = 'Prefecture'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))


class Bank(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Bank'
    id = Column(BigInteger, primary_key=True)
    code = Column(BigInteger)
    name = Column(String(255))


class BankAccount(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'BankAccount'
    id = Column(BigInteger, primary_key=True)
    bank_id = Column(BigInteger, ForeignKey("Bank.id"))
    bank = relationship("Bank", backref=backref('addresses', order_by=id))
    account_type = Column(Integer)
    account_number = Column(String(255))
    account_owner = Column(String(255))
    status = Column(Integer)


class PostCode(Base, BaseModel):
    """
            Table "public.post_code"
  Column   |          Type          | Modifiers
-----------+------------------------+-----------
 id        | bigint                 | not null
 version   | bigint                 | not null
 area      | character varying(255) | not null
 area_kana | character varying(255) | not null
 city      | character varying(255) | not null
 city_code | integer                | not null
 city_kana | character varying(255) | not null
 pref      | character varying(255) | not null
 pref_code | integer                | not null
 pref_kana | character varying(255) | not null
 zip7      | character varying(255) | not null
Indexes:
    "post_code_pkey" PRIMARY KEY, btree (id)
    "post_code_zip7" btree (zip7)
"""

    __tablename__ = 'PostCode'

    id          = Column(BigInteger, primary_key=True)
    version     = Column(BigInteger,  nullable=False)
    area        = Column(String(255), nullable=False)
    area_kana   = Column(String(255), nullable=False)
    city        = Column(String(255), nullable=False)
    city_code   = Column(BigInteger,  nullable=False)
    city_kana   = Column(String(255), nullable=False)
    pref        = Column(String(255), nullable=False)
    pref_code   = Column(BigInteger,  nullable=False)
    pref_kana   = Column(String(255), nullable=False)
    zip7        = Column(String(255), nullable=False)
