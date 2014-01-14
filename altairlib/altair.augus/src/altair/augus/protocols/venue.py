#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )

class _VenueProtocol(ProtocolBase):
    """会場図
    """
    pass

class _VenueRecord(RecordBase):
    """会場図座席レコード
    """
    pass

class VenueSyncRequestRecord(_VenueRecord):
    """会場図連携座席レコード
    """
    attributes = (
        'venue_code',
        'venue_name',
        'area_name',
        'info_name',
        'doorway_name',
        'priority',
        'floor',
        'column',
        'number',
        'block',
        'coordy',
        'coordx',        
        'coordy_whole',
        'coordx_whole',        
        'area_code',
        'info_code',
        'doorway_code',
        'venue_version',
        )

class VenueSyncResponseRecord(_VenueRecord):
    """会場図連携応答座席レコード
    """
    attributes = (
        'venue_code',
        'venue_name',
        'status',
        'venue_version',
        )

class VenueSyncRequest(_VenueProtocol):
    """会場図連携
    """
    record = VenueSyncRequestRecord
    pattern = '^RT(?P<customer_id>.{7})KAI(?P<venue_code>[^_]{0,9})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}KAI{venue_code:09d}_{created_at:14}.csv'

class VenueSyncResponse(_VenueProtocol):
    """会場図連携完了
    """
    record = VenueSyncResponseRecord
    pattern = '^RT(?P<customer_id>.{7})KAR(?P<venue_code>[^_]{0,9})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}KAR{venue_code:09d}_{created_at:14}.csv'
