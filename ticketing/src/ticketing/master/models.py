# encoding: utf-8
from ticketing.utils import StandardEnum
from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import join, backref, column_property

import sqlahelper

from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship

'''
 Master Data
'''
class Prefecture(object):
    __list = None
    __source = [
        (1, u'北海道'),
        (2, u'青森県'),
        (3, u'岩手県'),
        (4, u'宮城県'),
        (5, u'秋田県'),
        (6, u'山形県'),
        (7, u'福島県'),
        (8, u'茨城県'),
        (9, u'栃木県'),
        (10, u'群馬県'),
        (11, u'埼玉県'),
        (12, u'千葉県'),
        (13, u'東京都'),
        (14, u'神奈川県'),
        (15, u'新潟県'),
        (16, u'富山県'),
        (17, u'石川県'),
        (18, u'福井県'),
        (19, u'山梨県'),
        (20, u'長野県'),
        (21, u'岐阜県'),
        (22, u'静岡県'),
        (23, u'愛知県'),
        (24, u'三重県'),
        (25, u'滋賀県'),
        (26, u'京都府'),
        (27, u'大阪府'),
        (28, u'兵庫県'),
        (29, u'奈良県'),
        (30, u'和歌山県'),
        (31, u'鳥取県'),
        (32, u'島根県'),
        (33, u'岡山県'),
        (34, u'広島県'),
        (35, u'山口県'),
        (36, u'徳島県'),
        (37, u'香川県'),
        (38, u'愛媛県'),
        (39, u'高知県'),
        (40, u'福岡県'),
        (41, u'佐賀県'),
        (42, u'長崎県'),
        (43, u'熊本県'),
        (44, u'大分県'),
        (45, u'宮崎県'),
        (46, u'鹿児島県'),
        (47, u'沖縄県'),
        ]

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @classmethod
    def all(self):
        if self.__list is None:
            l = []
            for entry in self.__source:
                l.append(Prefecture(*entry))
            self.__list = l
        return self.__list

class Bank(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'Bank'
    id = Column(Identifier, primary_key=True)
    code = Column(BigInteger)
    name = Column(String(255))


class BankAccount(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'BankAccount'
    id = Column(Identifier, primary_key=True)
    bank_id = Column(Identifier, ForeignKey("Bank.id"))
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

    id          = Column(Identifier, primary_key=True)
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
