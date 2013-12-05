#-*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import HTTPBadRequest
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Venue, Seat, AugusVenue, AugusSeat, Organization
from .augus import SeatAugusSeatPairs

class IDownloadResource(Interface):
    cooperation_type = Attribute('')
    venue = Attribute('')
    pairs = Attribute('')

@implementer(IDownloadResource)
class DownloadResource(TicketingAdminResource):
    def __init__(self, request):
        super(DownloadResource, self).__init__(request)
        self.cooperation_type = None
        venue_id = None
        try:
            self.cooperation_type = long(request.params['cooperation_type'])
            venue_id = long(request.matchdict['venue_id'])
        except KeyError as err:
            raise HTTPBadRequest('Should be input parameter: {0}'.format(err))
        except (ValueError, TypeError) as err:
            raise HTTPBadRequest('Invalid type of parameter: {0}'.format(err))

        try:
            self.venue = self._get_venue(venue_id)
        except NoResultFound as err:
            raise HTTPNotFound('Not found venue: venue_id={0}'.format(venue_id))

        self.pairs = SeatAugusSeatPairs(self.venue.id)
        self.pairs.load()
        
    def _get_venue(self, venue_id):
        if venue_id is None:
            raise NoResultFound('Oh! venue_id is invalid: {0}'.format(venue_id))
            
        try:
            return Venue.query\
                        .join(Venue.organization)\
                        .filter(Organization.id==self.user.organization_id)\
                        .filter(Venue.id==venue_id)\
                        .one()
        except NoResultFound as err:
            raise
