from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, join, backref, column_property

import sqlahelper
session = sqlahelper.get_session()
Base = sqlahelper.get_base()

'''
 Master Data
'''
class Prefecture(Base):
    __tablename__ = 'Prefecture'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

    @staticmethod
    def all():
        return session.query(Prefecture).all()

    @staticmethod
    def all_tuple():
        return [(p.id, p.name) for p in session.query(Prefecture).all()]

    @staticmethod
    def get(prefecture_id):
        return session.query(Prefecture).filter(Prefecture.id == prefecture_id).first()


class Bank(Base):
    __tablename__ = 'Bank'
    id = Column(BigInteger, primary_key=True)
    code = Column(BigInteger)
    name = Column(String(255))

    @staticmethod
    def all_tuple():
        return [(p.id, p.name) for p in session.query(BankAccount).all()]

class BankAccount(Base):
    __tablename__ = 'BankAccount'
    id = Column(BigInteger, primary_key=True)
    back_id = Column(BigInteger, ForeignKey("Bank.id"))
    bank = relationship("Bank", backref=backref('addresses', order_by=id))
    account_type = Column(Integer)
    account_number = Column(String(255))
    account_owner = Column(String(255))
    updated_at = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Integer)


class PostCode(Base):
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