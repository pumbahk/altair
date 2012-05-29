# -*- coding: utf-8 -*-

from ticketing.models import BaseModel, MutationDict, JSONEncodedDict
from sqlalchemy import Table, Column, BigInteger, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, join, column_property, mapper

from datetime import datetime
from hashlib import md5

import sqlahelper

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

from ticketing.venues.models import Seat, SeatStatusEnum, SeatStatus
from ticketing.utils import StandardEnum

class SejTicket(BaseModel, Base):
    __tablename__       = 'SejTicketHistory'
    id                  = Column(BigInteger, primary_key=True)

    # shop_order_id
    order_id            = Column(String(12))
    # 払込票番号(haraikomi_no)
    haraikomi_no        = Column(String(13))
    # 引換票番号(hikae_no)
    hikae_no            = Column(String(13))
    # 払込票/引換票表示に指定するURL(url_info)
    url_info            = Column(String(128))
    #払込票/引換票表示の際にPOSTする情報(iraihyo_id_00)
    iraihyo_id_00       = Column(String(32))
    # 説明書含む発券枚数(ticket_count)
    ticket_count        = Column(Integer)
    # チケットの発券枚数(ticket_hon_count)
    ticket_hon_count    = Column(Integer)

    attributes          = Column(MutationDict.as_mutable(JSONEncodedDict(1024)))

    shori_kbn         = Column(Enum('1', '2', '3', '4'))

    # 決済に伊地知
    order_at            = Column(DateTime, nullable=True)
    # 支払日時間
    pay_at              = Column(DateTime, nullable=True)
    # 発券日時
    issue_at            = Column(DateTime, nullable=True)
    # キャンセル日時
    cancel_at           = Column(DateTime, nullable=True)

    updated_at          = Column(DateTime, nullable=True)
    created_at          = Column(DateTime, default=datetime.now)
