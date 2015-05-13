# -*- coding: utf-8 -*-


class LotEntriedEvent(object):
    def __init__(self, request, lot_entry):
        self.request = request
        self.lot_entry = lot_entry


class LotElectedEvent(object):
    def __init__(self, request, lot_wish):
        self.request = request
        self.lot_entry = lot_wish.lot_entry
        self.lot_wish = lot_wish


class LotRejectedEvent(object):
    def __init__(self, request, lot_entry):
        self.request = request
        self.lot_entry = lot_entry


class LotClosedEvent(object):
    def __init__(self, request, lot_entry):
        self.request = request
        self.lot_entry = lot_entry
