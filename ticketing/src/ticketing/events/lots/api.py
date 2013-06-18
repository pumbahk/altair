from .interfaces import ILotEntryStatus

def get_electing(request):
    return request.registry


def get_lot_entry_status(lot, request):
    reg = request.registry
    return reg.getMultiAdapter([lot, request], ILotEntryStatus)
