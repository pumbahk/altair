from pyramid.decorator import reify
from ticketing.core.models import Event, Performance
from ticketing.core import api as core_api
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

    @reify
    def host_base_url(self):
        return core_api.get_host_base_url(self.request)


class LotOptionSelectionResource(LotResource):
    def __init__(self, request):
        super(LotOptionSelectionResource, self).__init__(request)
        option_index = None
        try:
            option_index = int(self.request.matchdict.get('option_index'))
        except (TypeError, ValueError):
            pass
        if option_index is None:
            try:
                option_index = int(self.request.params.get('option_index'))
            except (TypeError, ValueError):
                pass
        if option_index > self.lot.limit_wishes:
            option_index = None
        self.option_index = option_index

        performance_id = None
        try:
            performance_id = int(self.request.params.get('performance_id'))
        except (ValueError, TypeError):
            pass

        if self.lot.sales_segment.performance_id != performance_id:
            performance_id = None

        self.performance = Performance.query.filter_by(id=performance_id).first()
