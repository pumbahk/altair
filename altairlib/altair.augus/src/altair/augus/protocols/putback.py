#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )

class _PutbackProtocol(ProtocolBase):
    """返券プロトコル
    """
    pass

class _PutbackRecord(RecordBase):
    """返券レコード
    """
    pass

class PutbackRequestRecord(_PutbackRecord):
    """返券要求レコード
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
    
class PutbackResponseRecord(_PutbackRecord):
    """返券応答レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'distribution_code',
        'putback_code',        
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
        'putback_status',
        'putback_type',
        )

class PutbackFinishRecord(_PutbackRecord):
    """返券完了レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'distribution_code',
        'putback_code',
        'seat_type_code',
        'unit_value_code',
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
        'status',
        'putback_type',
        )

class PutbackRequest(_PutbackProtocol):
    """返券要求
    """
    record = PutbackRequestRecord
    pattern = '^RT(?P<customer_id>.{7})HEY(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HEY{event_code:09d}_{date:12}_{created_at:14}.csv'

class PutbackResponse(_PutbackProtocol):
    """返券応答
    """
    record = PutbackResponseRecord
    pattern = '^RT(?P<customer_id>.{7})HEN(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HEN{event_code:09d}_{date:12}_{created_at:14}.csv'
        
class PutbackFinish(_PutbackProtocol):
    """返券完了
    """
    record = PutbackFinishRecord    
    pattern = '^RT(?P<customer_id>.{7})HEK(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HEK{event_code:09d}_{date:12}_{created_at:14}.csv'
