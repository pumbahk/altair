# -*- coding: utf-8 -*-
from .interfaces import ILotEntryStatus
from altair.app.ticketing.carturl.api import get_lots_cart_url_builder
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Event
from altair.app.ticketing.lots.models import Lot

def get_electing(request):
    return request.registry

def get_lot_entry_status(lot, request):
    reg = request.registry
    return reg.getMultiAdapter([lot, request], ILotEntryStatus)

def get_lots_cart_url(request, event_id, lot_id):
    event = get_db_session(request, name="slave").query(Event).filter(Event.id==event_id).first()
    lot = get_db_session(request, name="slave").query(Lot).filter(Lot.id==lot_id).first()
    cart_url = get_lots_cart_url_builder(request).build(request, event, lot)
    return cart_url
