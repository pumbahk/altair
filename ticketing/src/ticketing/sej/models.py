# -*- coding: utf-8 -*-

from ticketing.models import BaseModel, MutationDict, JSONEncodedDict, relationship
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import join, column_property, mapper

from datetime import datetime
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class SejTicket(BaseModel, Base):
    __tablename__       = 'SejTicket'
    id                  = Column(Integer, primary_key=True)

    # shop_order_id
    order_id            = Column(String(12))
    exchange_number     = Column(String(13))
    billing_number      = Column(String(13))

    exchange_sheet_url  = Column(String(128))
    exchange_sheet_number  \
                        = Column(String(32))

    total_price         = Column(DECIMAL)
    ticket_price        = Column(DECIMAL)
    commission_fee      = Column(DECIMAL)

    total_ticket_count  = Column(Integer)
    ticket_count        = Column(Integer)
    return_ticket_count = Column(Integer)

    request_params      = Column(MutationDict.as_mutable(JSONEncodedDict(4000)))
    attributes          = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    process_id          = Column(String(12))
    process_type        = Column(Enum('1', '2', '3', '4'))

    notification_type   = Column(Enum('1', '31'))

    pay_store_number    = Column(String(6))
    pay_store_name      = Column(String(36))

    ticketing_store_number\
                        = Column(String(6))
    ticketing_store_name= Column(String(36))

    processed_at        = Column(DateTime, nullable=True)

    # 決済に日時
    order_at            = Column(DateTime, nullable=True)
    # 支払日時
    pay_at              = Column(DateTime, nullable=True)
    # 発券日時
    issue_at            = Column(DateTime, nullable=True)
    # キャンセル日時
    cancel_at           = Column(DateTime, nullable=True)

    updated_at          = Column(DateTime, nullable=True)
    created_at          = Column(DateTime, default=datetime.now)


