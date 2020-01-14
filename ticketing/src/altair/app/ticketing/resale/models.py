# -*- coding: utf-8 -*-

import logging

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.saannotation import AnnotatedColumn

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, DateTime, Unicode, Numeric, Integer

logger = logging.getLogger(__name__)

class SentStatus:
    not_sent = 1
    sent = 2
    send_required = 3
    fail = 4
    unknown = 5

class ResaleRequestStatus:
    waiting = 1
    sold = 2
    back = 3
    cancel = 4
    unknown = 5


class ResaleSegment(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ResaleSegment'
    id = Column(Identifier, primary_key=True)
    performance_id = Column(Identifier, nullable=False)
    resale_performance_id = Column(Identifier, nullable=False)
    sent_at = AnnotatedColumn(DateTime, nullable=True, _a_label=u'連携日時')
    sent_status = Column(Integer, nullable=False, default=1)
    reception_start_at = AnnotatedColumn(DateTime, nullable=False, _a_label=u'申込開始日時')
    reception_end_at = AnnotatedColumn(DateTime, nullable=False, _a_label=u'申込終了日時')
    resale_start_at = AnnotatedColumn(DateTime, nullable=False, _a_label=u'リセール開始日時', default=None)
    resale_end_at = AnnotatedColumn(DateTime, nullable=False, _a_label=u'リセール終了日時', default=None)

    @property
    def get_performance_id(self):
        return self.performance_id

class ResaleRequest(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'ResaleRequest'
    id = Column(Identifier, primary_key=True)
    resale_segment_id = Column(Identifier, ForeignKey('ResaleSegment.id', ondelete='CASCADE'), nullable=False)
    resale_segment = relationship("ResaleSegment", backref="resale_requests")
    ordered_product_item_token_id = Column(Identifier)
    bank_code = AnnotatedColumn(Unicode(32), nullable=False, _a_label=u'銀行コード')
    bank_branch_code = AnnotatedColumn(Unicode(32), nullable=False, _a_label=u'支店コード')
    account_type = AnnotatedColumn(Unicode(64), nullable=False, default=u'', _a_label=u'銀行口座種別')
    account_number = AnnotatedColumn(Unicode(32), nullable=False, _a_label=u'銀行口座番号')
    account_holder_name = AnnotatedColumn(Unicode(255), nullable=False, _a_label=(u'名義人'))
    total_amount = AnnotatedColumn(Numeric(precision=16, scale=2), nullable=False, _a_label=u'振込合計金額')
    sold_at = AnnotatedColumn(DateTime, nullable=True, _a_label=u'リセール日時')
    status = Column(Integer, nullable=False, default=1)
    sent_at = AnnotatedColumn(DateTime, nullable=True, _a_label=u'連携日時')
    sent_status = Column(Integer, nullable=False, default=1)
    stock_count_at = AnnotatedColumn(DateTime, nullable=True, default=None)

    @property
    def get_performance_id(self):
        return self.resale_segment.get_performance_id if self.resale_segment else None

    @property
    def label_attribute(self):
        if self.status == ResaleRequestStatus.waiting:
            return u'warning'
        elif self.status == ResaleRequestStatus.sold:
            return u'success'
        elif self.status == ResaleRequestStatus.back:
            return u'info'
        elif self.status == ResaleRequestStatus.cancel:
            return u'important'
        else:
            return u''

    @property
    def verbose_status(self):
        if self.sent_status == SentStatus.sent:
            verbose_status = u''
        else:
            verbose_status = u'（仮）'

        if self.status == ResaleRequestStatus.waiting:
            verbose_status = u'リセール中'
        elif self.status == ResaleRequestStatus.sold:
            verbose_status += u'リセール済み'
        elif self.status == ResaleRequestStatus.back:
            verbose_status += u'リセール返却'
        elif self.status == ResaleRequestStatus.cancel:
            verbose_status += u'リセールキャンセル'
        else:
            verbose_status = u'予想外エラー'

        return verbose_status

    @property
    def resale_status_label(self):
        if self.status == ResaleRequestStatus.waiting:
            return u'リセール出品中'
        if self.status == ResaleRequestStatus.sold:
            return u'リセール成立' if self.sent_status == SentStatus.sent else u'リセール出品中'
        if self.status == ResaleRequestStatus.back:
            return u'リセール不成立' if self.sent_status == SentStatus.sent else u'リセール出品中'
        if self.status == ResaleRequestStatus.cancel:
            return u'リセールキャンセル' if self.sent_status == SentStatus.sent else u'リセール出品中'
        if self.status == ResaleRequestStatus.unknown:
            return u'準備中' if self.sent_status == SentStatus.sent else u'リセール出品中'
        return u''

    @property
    def has_send_to_resale_status(self):
        if self.sent_status in [SentStatus.not_sent, SentStatus.sent]:
            return self.status not in [ResaleRequestStatus.back, ResaleRequestStatus.cancel]
        return True
