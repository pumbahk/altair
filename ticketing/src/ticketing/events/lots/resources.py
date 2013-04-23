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
        lot = self.lot
        if lot is None:
            return None
        event_id = None
        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass
        if event_id is not None:
            if lot.event_id != event_id:
                return None
        return lot.event
