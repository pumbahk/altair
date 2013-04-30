from ticketing.core.models import Event
from ticketing.lots.models import Lot

from ticketing.resources import TicketingAdminResource

class LotResource(TicketingAdminResource):
    @property
    def lot(self):
        lot_id = None
        try:
            lot_id = long(self.request.matchdict.get('lot_id'))
        except (TypeError, ValueError):
            pass
        if not lot_id:
            return None

        return Lot.query.filter(Lot.id==lot_id).first()

    @property
    def event(self):
        event_id = None
        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass
        lot = self.lot
        if event_id is not None:
            if lot is not None and lot.event_id == event_id:
                event = lot.event
            else:
                event = Event.query.filter(Event.id == event_id).first()
        else:
            if lot is not None:
                event = lot.event
            else:
                event = None
        return event
