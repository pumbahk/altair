#-*- coding: utf-8 -*-
from .common import (
    ProtocolBase,
    RecordBase,
    )

class _TicketProtocol(ProtocolBase):
    """チケット関連プロトコル
    """
    pass

class _TicketRecord(RecordBase):
    """チケットレコード
    """
    pass

class TicketSyncRequestRecord(_TicketRecord):
    """チケットレコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'venue_code',
        'seat_type_code',
        'unit_value_code',
        'seat_type_name',
        'unit_value_name',
        'seat_type_classif',
        'value',
        )

class TicketSyncRequest(_TicketProtocol):
    """チケット(席種)連携
    """
    record = TicketSyncRequestRecord
    pattern = '^RT(?P<customer_id>.{7})TKT(?P<event_code>[^_]{0,9})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}TKT{event_code:09d}_{created_at:14}.csv'

