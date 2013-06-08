# -*- coding: utf-8 -*-
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound
from pyramid.traversal import DefaultRootFactory
from pyramid.decorator import reify
from ticketing.core.models import Event, Performance, Organization
from ticketing.cart import api as cart_api
from .exceptions import OutTermException
from .models import Lot

def lot_resource_factory(request):
    if request.matchdict is None:
        return DefaultRootFactory(request)

    context = LotResource(request)
    if context.lot:
        if not context.lot.available_on(datetime.now()):
            raise OutTermException(lot_name=context.lot.name,
                                   from_=context.lot.start_at,
                                   to_=context.lot.end_at)
    return context



class LotResource(object):
    def __init__(self, request):
        self.request = request

        self.organization = self.request.organization

        from ticketing.models import DBSession
        DBSession.merge(self.organization)

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

    def authenticated_user(self):
        # XXX: とりあえずダミー
        return { 'is_guest': True }

    @reify
    def host_base_url(self):
        return cart_api.get_host_base_url(self.request)


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
