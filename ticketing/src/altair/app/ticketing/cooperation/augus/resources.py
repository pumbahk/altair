#-*- coding: utf-8 -*-
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from sqlalchemy import (
    or_,
    and_,
    )
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Venue,
    AugusVenue,
    Event,
    AugusTicket,
    AugusPerformance,
    )
from .utils import (
    RequestAccessor,
    )
from .errors import (
    NoSeatError,
    BadRequest,
    )


class AugusVenueListRequestAccessor(RequestAccessor):
    in_matchdict = {'augus_venue_code': int}

class AugusVenueListResource(TicketingAdminResource):
    accessor_factory = AugusVenueListRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)        
        accessor = self.accessor_factory(request)
        self.augus_venue_code = accessor.augus_venue_code
        self.augus_venues = AugusVenue.query.filter(AugusVenue.code==self.augus_venue_code).all()
        if 0 == len(self.augus_venues):
            raise HTTPNotFound(
                'Not found AugusVenue: AugusVenue.code == {} is not found.'.format(
                    self.augus_venue_code))

class AugusVenueRequestAccessor(RequestAccessor):
    in_matchdict = {'augus_venue_code': int,
                    'augus_venue_version': int,
                    }
    
class AugusVenueResource(TicketingAdminResource):
    accessor_factory = AugusVenueRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)        
        accessor = self.accessor_factory(request)
        self.augus_venue_code = accessor.augus_venue_code
        self.augus_venue_version = accessor.augus_venue_version
        try:
            self.augus_venue = AugusVenue\
                .query.filter(AugusVenue.code==self.augus_venue_code)\
                      .filter(AugusVenue.version==self.augus_venue_version)\
                      .one()
        except (MultipleResultsFound, NoResultFound):
            raise HTTPNotFound('The AugusVenue not found or multiply: code={}, version={}'.format(
                self.augus_venue_code, self.augus_venue_version))
        
class VenueRequestAccessor(RequestAccessor):
    in_matchdict = {'venue_id': int}
        
    
class VenueResource(TicketingAdminResource):
    accessor_factory = VenueRequestAccessor    
    def __init__(self, request):
        super(type(self), self).__init__(request)
        accessor = self.accessor_factory(request)
        try:
            self.venue = Venue.query.filter(Venue.id==accessor.venue_id)\
                                    .filter(Venue.organization_id==self.user.organization_id)\
                                    .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The venue_id = {} is not found or multiply.'.format(request.matchdict.get('venue_id')))
        self.augus_venues = AugusVenue.query.filter(AugusVenue.venue_id==self.venue.id).all()

class SeatTypeRequestAccessor(RequestAccessor):
    in_matchdict = {'event_id': int}

class SeatTypeResource(TicketingAdminResource):
    accessor_factory = SeatTypeRequestAccessor    
    def __init__(self, request):
        super(type(self), self).__init__(request)
        accessor = self.accessor_factory(request)
        try:
            self.event = Event.query.filter(Event.id==accessor.event_id)\
                                    .filter(Venue.organization_id==self.user.organization_id)\
                                    .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The event_id = {} is not found or multiply.'.format(request.matchdict.get('event_id')))

        performance_ids = [pfc.id for pfc in self.event.performances]
        ag_performances = AugusPerformance.query.filter(AugusPerformance.performance_id.in_(performance_ids)).all()
        if ag_performances:
            ag_event_code = ag_performances[0].augus_event_code
            ag_performance_codes = [ag_performance.augus_performance_code for ag_performance in ag_performances]
            ag_ticekts = AugusTicket.query.filter(AugusTicket.augus_performance_code.in_(ag_performance_codes)).all()
            ag_tickets = [ag_ticket for ag_ticekt in ag_tickets if ag_ticket.augus_event_code == ag_event_code]
            self.ag_ticekts = ag_tickets
        else:
            self.ag_tickets = []
