#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )

class _AchievementRecord(RecordBase):
    """販売実績レコード
    """
    pass

class _AchievementProtocol(ProtocolBase):
    """販売実績
    """    
    pass


class AchievementRequestRecord(_AchievementRecord):
    """販売実績要求レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'date',
        'start_on',
        'event_name',
        'performance_name',
        'venue_name',
        )

class AchievementResponseRecord(_AchievementRecord):
    """販売実績応答レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'trader_code',
        'distribution_code',
        'seat_type_code',
        'unit_value_code',
        'date',
        'start_on',
        'reservation_number',
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
        'unit_value',
        'processed_at',
        'achievement_status',
        )

class AchievementRequest(_AchievementProtocol):
    """販売実績要求
    """
    record = AchievementRequestRecord
    pattern = '^RT(?P<customer_id>.{7})JIS(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}JIS{event_code:09d}_{date:12}_{created_at:14}.csv'

class AchievementResponse(_AchievementProtocol):
    """販売実績応答
    """
    record = AchievementResponseRecord
    pattern = '^RT(?P<customer_id>.{7})HAN(?P<event_code>[^_]{0,9})_(?P<date>\d{12})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}HAN{event_code:09d}_{date:12}_{created_at:14}.csv'

