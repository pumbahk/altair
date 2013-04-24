from pyramid.decorator import reify
from ticketing.core.models import Event
from .models import Lot

class LotResource(object):
    def __init__(self, request):
        self.request = request

    @reify
    def event(self):
        event_id = self.request.matchdict['event_id']
        return Event.query.filter(Event.id==event_id).one()
        

    @reify
    def lot(self):
        event_id = self.request.matchdict.get('event_id')
        lot_id = self.request.matchdict.get('lot_id')
        lot = Lot.query.filter(
            Lot.event_id==event_id
            ).filter(
            Lot.id==lot_id,
            ).first()
        return lot
