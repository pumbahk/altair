# -*- coding: utf-8 -*-

from ticketing.models import BaseModel, LogicallyDeleted, WithTimestamp, MutationDict, JSONEncodedDict, relationship
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey, Enum, DECIMAL
from sqlalchemy.orm import relationship, join, column_property, mapper, backref

from datetime import datetime
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

class SejNotification(BaseModel, WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejNotification'

    id                      = Column(Integer, primary_key=True)

    notification_type       = Column(Enum('1', '31', '72', '73'))
    process_number          = Column(String(12))
    payment_type            = Column(Enum('1', '2', '3', '4'))
    payment_type_new        = Column(Enum('1', '2', '3', '4'), nullable=True)

    shop_id                 = Column(String(5))
    order_id                = Column(String(12))

    exchange_number         = Column(String(13))
    exchange_number_new     = Column(String(13), nullable=True)
    billing_number          = Column(String(13))
    billing_number_new      = Column(String(13), nullable=True)

    exchange_sheet_url      = Column(String(128), nullable=True)
    exchange_sheet_number   = Column(String(32), nullable=True)

    total_price             = Column(DECIMAL)
    total_ticket_count      = Column(Integer)

    ticket_count            = Column(Integer)
    return_ticket_count     = Column(Integer)

    ticketing_due_datetime  = Column(DateTime, nullable=True)
    ticketing_due_datetime_new = Column(DateTime, nullable=True)

    pay_store_number        = Column(String(6))
    pay_store_name          = Column(String(36))

    ticketing_store_number  = Column(String(6))
    ticketing_store_name    = Column(String(36))

    cancel_reason           = Column(String(2), nullable=True)
    processed_at            = Column(DateTime, nullable=True)

    barcode_numbers         = Column(MutationDict.as_mutable(JSONEncodedDict(4096)), nullable=True)

    processed_at            = Column(DateTime, nullable=True)
    signature               = Column(String(32))

class SejTicketFile(BaseModel, WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejTicketFile'

    id                      = Column(Integer, primary_key=True)

    notification_type       = Column(Enum('51', '61', '91', '92', '94', '95', '96', '97', '98'))
    payment_type            = Column(Enum('1', '2', '3', '4'))

    shop_id                 = Column(String(5))
    order_id                = Column(String(12))

    exchange_number         = Column(String(13), nullable=True)
    billing_number          = Column(String(13), nullable=True)

    exchange_sheet_url      = Column(String(128), nullable=True)
    exchange_sheet_number   = Column(String(32), nullable=True)

    total_ticket_count      = Column(Integer, nullable=True)
    ticket_count            = Column(Integer, nullable=True)
    return_ticket_count     = Column(Integer, nullable=True)

    ticket_barcode_number   = Column(String(13))

    receipt_amount          = Column(DECIMAL, nullable=True)
    refund_ticket_price     = Column(DECIMAL, nullable=True)
    refund_other_price      = Column(DECIMAL, nullable=True)

    received_at             = Column(DateTime, nullable=True)
    process_at              = Column(DateTime, nullable=True)

    cancel_reason           = Column(Enum('1', '2', '3', '4'))
    refund_status           = Column(Enum('1', '2', '3', '4'))
    refund_cancel_reason    = Column(Enum('1', '2', '3', '4'))

    refund_cancel_at        = Column(DateTime, nullable=True)

    attributes              = Column(MutationDict.as_mutable(JSONEncodedDict(4096)))
    signature               = Column(String(32))


class SejOrder(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejOrder'
    id                      = Column(Integer, primary_key=True)

    order_id                = Column(String(12))
    exchange_number         = Column(String(13))
    billing_number          = Column(String(13))

    exchange_sheet_url      = Column(String(128))
    exchange_sheet_number   = Column(String(32))

    total_price             = Column(DECIMAL)
    ticket_price            = Column(DECIMAL)
    commission_fee          = Column(DECIMAL)

    total_ticket_count      = Column(Integer)
    ticket_count            = Column(Integer)
    return_ticket_count     = Column(Integer)

    process_id              = Column(String(12))
    payment_type            = Column(Enum('1', '2', '3', '4'))

    pay_store_number        = Column(String(6))
    pay_store_name          = Column(String(36))

    cancel_reason           = Column(String(2))

    ticketing_store_number  = Column(String(6))
    ticketing_store_name    = Column(String(36))

    processed_at            = Column(DateTime, nullable=True)

    # 決済に日時
    order_at                = Column(DateTime, nullable=True)
    # 支払日時
    pay_at                  = Column(DateTime, nullable=True)
    # 発券日時
    issue_at                = Column(DateTime, nullable=True)
    # キャンセル日時
    cancel_at               = Column(DateTime, nullable=True)

    request_params          = Column(MutationDict.as_mutable(JSONEncodedDict(4096)))
    callback_params         = Column(MutationDict.as_mutable(JSONEncodedDict(4096)))


class SejTicket(BaseModel,  WithTimestamp, LogicallyDeleted, Base):
    __tablename__           = 'SejTicket'

    id                      = Column(Integer, primary_key=True)
    ticket_type             = Column(Enum('1', '2', '3', '4'))
    barcode_number          = Column(String(13))
    event_name              = Column(String(40))
    performance_name        = Column(String(40))
    performance_datetime    = Column(DateTime)
    ticket_template_id      = Column(String(10))
    ticket_data_xml         = Column(String(5000))

    ticket                  = relationship("SejOrder", backref='tickets')
    ticket_id               = Column(Integer, ForeignKey("SejOrder.id"), nullable=True)

    ticket_idx              = Column(Integer)



