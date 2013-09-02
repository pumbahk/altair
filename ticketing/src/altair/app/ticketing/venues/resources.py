# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Venue

class VenueAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(VenueAdminResource, self).__init__(request)

        venue_id = None

        if not self.user:
            return

        try:
            venue_id = long(request.matchdict.get('venue_id'))
        except (TypeError, ValueError):
            pass

        if venue_id is not None:
            try:
                self.venue = Venue.query.filter_by(id=venue_id)\
                    .filter_by(organization_id=self.user.organization_id).one()
            except NoResultFound:
                raise HTTPNotFound()
        else:
            self.venue = None
