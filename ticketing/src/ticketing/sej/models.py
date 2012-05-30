# -*- coding: utf-8 -*-

from ticketing.models import BaseModel, MutationDict, JSONEncodedDict
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import relationship, join, column_property, mapper

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

    '''
    shop_order_id       = order_id

    goukei_kingaku      = total_price

    X_ticket_daikin     = ticket_price
    X_ticket_kounyu_daikin = commission_fee

    url_info            = exchange_sheet_url
    iraihyo_id_00       = exchange_sheet_number

    hikikae_no          = exchange_number
    haraikomi_no        = billing_number

    ticket_count        = total_ticket_count
    ticket_num          = ticket_count
    kaishu_cnt          = return_ticket_count

    shori_id            = process_id
    shori_kbn           = process_type
    tuchi_type          = notification_type

    pay_mise_no         = pay_store_name
    pay_mise_name       = pay_store_name

    hakken_mise_no      = ticketing_store_number
    hakken_mise_name    = ticketing_store_name

    shori_time          = process_time
    '''

