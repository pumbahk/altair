#-*- coding: utf-8 -*-
import time
import datetime
from .common import (
    ProtocolBase,
    RecordBase,
    )

class _PerformanceProtocol(ProtocolBase):
    """公演連携規約
    """
    pass

class _PerformanceRecord(RecordBase):
    """公演レコード
    """
    pass

class PerformanceSyncRequestRecord(_PerformanceRecord):
    """公演連携要求レコード
    """
    attributes = (
        'event_code',
        'performance_code',
        'venue_code',
        'venue_name',
        'event_name',
        'performance_name',
        'date',
        'open_on',
        'start_on',
        'venue_version',
        )
    
    def _str2datetime(self, txt):
        st = time.strptime(txt, '%Y%m%d%H%M')
        return datetime.datetime(*st[:5])

    @property
    def open_on_datetime(self):
        return self._str2datetime(self.date + self.open_on)

    @property
    def start_on_datetime(self):
        return self._str2datetime(self.date + self.start_on)


class PerformanceSyncRequest(_PerformanceProtocol):
    """公演連携要求
    """
    record = PerformanceSyncRequestRecord
    pattern = '^RT(?P<customer_id>.{7})GME(?P<event_code>[^_]{0,9})_(?P<created_at>\d{14})\.csv$'
    fmt = 'RT{customer_id:07d}GME{event_code:09d}_{created_at:14}.csv'
