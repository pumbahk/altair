class LotEntriedEvent(object):
    def __init__(self, request, lot_entry):
        self.request = request
        self.lot_entry = lot_entry
