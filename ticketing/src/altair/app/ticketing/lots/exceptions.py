# -*- coding:utf-8 -*-


class LotEntryDeletionError(Exception):
    """抽選申込の削除ができない"""


class NotElectedException(Exception):
    """ 当選していない抽選 """


class OutTermException(Exception):
    def __init__(self, lot):
        super(OutTermException, self).__init__()
        self.lot = lot


class OverEntryLimitException(Exception):
    def __init__(self, entry_limit, *args, **kwargs):
        super(OverEntryLimitException, self).__init__(*args, **kwargs)
        self.entry_limit = entry_limit


class OverEntryLimitPerPerformanceException(OverEntryLimitException):
    def __init__(self, performance_name, entry_limit, *args, **kwargs):
        super(OverEntryLimitPerPerformanceException, self).__init__(entry_limit, *args, **kwargs)
        self.performance_name = performance_name
