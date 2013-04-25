from pyramid.decorator import reify
from ticketing.core.models import Event, Performance, Organization
from ticketing.core import api as core_api
from .models import Lot

class LotResource(object):
    def __init__(self, request):
        self.request = request

        self.organization = core_api.get_organization(self.request)

        event_id = self.request.matchdict.get('event_id')
        self.event = Event.query \
            .filter(Event.id==event_id) \
            .filter(Organization.id==self.organization.id) \
            .first()

        lot = None 
        if self.event is not None: 
            lot_id = self.request.matchdict.get('lot_id')
            lot = Lot.query \
                .filter(Lot.event_id==event_id) \
                .filter(Lot.id==lot_id) \
                .first()
        self.lot = lot

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

        self.performance = Performance.query \
            .filter(Performance.id == performance_id) \
            .filter(Performance.event_id == self.event.id) \
            .first()
