# -*- coding: utf-8 -*-

from altair.app.ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier
from altair.app.ticketing.core.models import SalesSegment
from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Numeric, Integer, String
from standardenum import StandardEnum


class PriceBatchUpdateTaskStatusEnum(StandardEnum):
    Waiting = 0
    Updating = 1
    Updated = 2
    Canceled = 3
    Aborted = 4


class PriceBatchUpdateErrorEnum(StandardEnum):
    PDU_E_001 = {
        'msg': u'変更内容が見つかりませんでした。'
    }
    PDU_E_002 = {
        'msg': u'全ての商品で価格変更に失敗しました。'
    }
    PDU_W_001 = {
        'msg': u'一部の商品の価格変更に失敗しました。'
    }
    PDU_PE_E_001 = {
        'msg': u'指定された販売区分が存在しません。'
    }
    PDU_PE_E_002 = {
        'msg': u'商品が存在しません。'
    }
    PDU_PE_E_003 = {
        'msg': u'名前が同じ商品が複数存在します。'
    }
    PDU_PE_E_004 = {
        'msg': u'商品明細が複数存在します。'
    }
    PDU_PE_E_005 = {
        'msg': u'予期せぬエラーにより終了しました。'
    }


class PriceBatchUpdateTask(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PriceBatchUpdateTask'

    id = Column(Identifier, primary_key=True)
    organization_id = Column(Identifier, ForeignKey('Organization.id', ondelete='CASCADE'), nullable=False)
    performance_id = Column(Identifier, ForeignKey('Performance.id', ondelete='CASCADE'), nullable=False)
    operator_id = Column(Identifier, ForeignKey('Operator.id', ondelete='CASCADE'), nullable=False)
    status = Column(Integer, nullable=False)
    count_updated = Column(Integer, nullable=True)
    error = Column(String(20), nullable=True)

    organization = relationship('Organization')
    performance = relationship('Performance')
    operator = relationship('Operator')
    entries = relationship('PriceBatchUpdateEntry', backref=backref('task'),
                           primaryjoin=lambda:
                           and_(PriceBatchUpdateTask.id == PriceBatchUpdateEntry.price_batch_update_task_id,
                                PriceBatchUpdateEntry.deleted_at.is_(None)))

    @property
    def sales_segments(self):
        sales_segments_dict = dict()
        for entry in self.entries:
            sales_segments_dict[entry.sales_segment_id] = entry.sales_segment

        return sales_segments_dict.values() if len(sales_segments_dict) > 0 else []


class PriceBatchUpdateEntry(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    __tablename__ = 'PriceBatchUpdateEntry'

    id = Column(Identifier, primary_key=True)
    price_batch_update_task_id = Column(Identifier,
                                        ForeignKey('PriceBatchUpdateTask.id', ondelete='CASCADE'), nullable=False)
    product_name = Column(String(255), nullable=False)
    price = Column(Numeric(precision=16, scale=2), nullable=False)
    sales_segment_id = Column(Identifier, ForeignKey('SalesSegment.id', ondelete='CASCADE'), nullable=False)
    error = Column(String(20), nullable=True)

    sales_segment = relationship('SalesSegment',
                                 primaryjoin=lambda:
                                 and_(SalesSegment.id == PriceBatchUpdateEntry.sales_segment_id,
                                      SalesSegment.deleted_at.is_(None)))

