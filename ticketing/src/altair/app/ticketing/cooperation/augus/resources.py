#-*- coding: utf-8 -*-
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    )
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Venue,
    )
from .utils import (
    RequestAccessor,
    )
from .errors import (
    NoSeatError,
    BadRequest,
    )

class AugusVenueRequestAccessor(RequestAccessor):
    in_matchdict = {'venue_id': int}

    
class AugusVenueResource(TicketingAdminResource):
    def __init__(self, request):
        super(type(self), self).__init__(request)

        accessor = AugusVenueRequestAccessor(request)
        try:
            self.venue = Venue.query.filter(Venue.id==accessor.venue_id)\
                                    .filter(Venue.organization_id==self.user.organization_id)\
                                    .one()
        except (BadRequest, NoResultFound) as err:
            raise HTTPNotFound('The venue_id = {} is not found.'.format(request.matchdict.get('venue_id')))
            
        # self.pairs = SeatAugusSeatPairs(self.venue.id)            
        # try:
        #     self.pairs.load()
        # except BadRequest as err:
        #     raise HTTPBadRequest(err)
