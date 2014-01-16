# -*- coding: utf-8 -*-
from .interfaces import ILotEntryStatus

def get_electing(request):
    return request.registry

def get_lot_entry_status(lot, request):
    reg = request.registry
    return reg.getMultiAdapter([lot, request], ILotEntryStatus)

def get_lotting_announce_timezone(timezone):
    label = u""
    labels = dict(morning=u'午前', day=u'昼以降', evening=u'夕方以降', night=u'夜', next_morning=u'明朝')
    if timezone in labels:
        label = labels[timezone]
    return label
