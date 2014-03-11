#-*- coding: utf-8 -*-
from pyramid.decorator import reify
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from altair.app.ticketing.core.models import (
    Venue,
    GettiiVenue,
    )
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.cooperation.utils import RequestAccessor

class VenueRequestAccessor(RequestAccessor):
    in_matchdict = {'venue_id': int,
                    }

class VenueResource(TicketingAdminResource):
    accessor_factory = VenueRequestAccessor
    def __init__(self, request):
        super(type(self), self).__init__(request)
        self.accessor = self.accessor_factory(request)

    @reify
    def venue(self):
        try:
            return Venue.query.filter(Venue.id==self.accessor.venue_id)\
                              .filter(Venue.organization_id==self.organization.id)\
                              .one()
        except (MultipleResultsFound, NoResultFound) as err:
            raise HTTPNotFound('The venue_id = {} is not found or multiply.'.format(self.accessor.venue_id))

    @reify
    def external_venues(self):
        return GettiiVenue.query.filter(GettieVenue.venue_id==self.venue.id)\
                                .filter(Venue.organization_id==self.organization.id)\
                                .all()
