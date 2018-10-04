#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )
import time
import datetime


class _DistributionRecord(RecordBase):
    """配券レコード
    """
    pass


class _DistributionProtocol(ProtocolBase):
    """配券
    """
    pass


class DistributionSyncRequestRecord(_DistributionRecord):
    """配券連携 初期/追加 共用 レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'distribution_code',
        'seat_type_code',
        'unit_value_code',
        'date',
        'start_on',
        'block',
        'coordy',
        'coordx',
        'area_code',
        'info_code',
        'floor',
        'column',
        'number',
        'seat_type_classif',
        'seat_count',
        )

    def _str2datetime(self, txt):
        st = time.strptime(txt, '%Y%m%d%H%M')
        return datetime.datetime(*st[:5])

    @property
    def start_on_datetime(self):
        return self._str2datetime(self.date + self.start_on)


class DistributionWithNumberedTicketSyncRequestRecord(_DistributionRecord):
    """配券連携 初期/追加 共用 レコード 整理券フォーマット
    """
    attributes = (
        'event_code',
        'performance_code',
        'distribution_code',
        'seat_type_code',
        'unit_value_code',
        'date',
        'start_on',
        'block',
        'coordy',
        'coordx',
        'area_code',
        'info_code',
        'floor',
        'column',
        'number',
        'ticket_number',
        'seat_type_classif',
        'seat_count',
        )

    def _str2datetime(self, txt):
        st = time.strptime(txt, '%Y%m%d%H%M')
        return datetime.datetime(*st[:5])

    @property
    def start_on_datetime(self):
        return self._str2datetime(self.date + self.start_on)


class DistributionSyncResponseRecord(_DistributionRecord):
    """配券完了 初期/追加 共用 レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'distribution_code',
        'status',
        )


class DistributionSyncRequest(_DistributionProtocol):
    """配券連携 初期/追加 共用
    """
    record = DistributionSyncRequestRecord
    pattern = '^RT(?P<customer_id>.{7})HAI(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HAI{event_code:09d}_{date:12}_{created_at:14}.csv'


class DistributionWithNumberedTicketSyncRequest(DistributionSyncRequest):
    """配券連携 初期/追加 共用 整理券フォーマット
    """
    # tkt5866 あえてALLには追加しない。既存処理を考慮し、AugusParser.get_protocolで拾われないようにするため
    record = DistributionWithNumberedTicketSyncRequestRecord


class DistributionSyncResponse(_DistributionProtocol):
    """配券完了
    """
    record = DistributionSyncResponseRecord
    pattern = '^RT(?P<customer_id>.{7})HAR(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HAR{event_code:09d}_{date:12}_{created_at:14}.csv'
