#-*- coding: utf-8 -*-
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Venue,
    AugusVenue,
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
