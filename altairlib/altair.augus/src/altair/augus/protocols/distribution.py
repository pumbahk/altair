#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )

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


class DistributionSyncResponse(_DistributionProtocol):
    """配券完了
    """
    record = DistributionSyncResponseRecord
    pattern = '^RT(?P<customer_id>.{7})HAR(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HAR{event_code:09d}_{date:12}_{created_at:14}.csv'
