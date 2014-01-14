#-*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    )
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Venue,
    Seat,
    AugusVenue,
    AugusSeat,
    Organization,
    )
from .augus2 import SeatAugusSeatPairs


class ICooperationResource(Interface):
    cooperation_type = Attribute('')
    venue = Attribute('')
    pairs = Attribute('')


class BadRequest(Exception):
    pass

class NotFound(Exception):
    pass


class _CooperationResourceMixin(object):
    def _load_common(self, request):
        accessor = RequestAccessor(request)
        organization_id = self.user.organization_id
        try:
            self.cooperation_type = accessor.get_cooperation_type()
            self.venue = accessor.get_venue(organization_id=organization_id)
        except BadRequest as err:
            raise HTTPBadRequest(err.message)
        except NotFound as err:
            raise HTTPNotFound(err.message)
        
@implementer(ICooperationResource)
class CooperationResource(TicketingAdminResource, _CooperationResourceMixin):
    def __init__(self, request):
        super(CooperationResource, self).__init__(request)
        self._load_common(request)        
        self.pairs = SeatAugusSeatPairs(self.venue.id)
        self.pairs.load()





class RequestAccessor(object):
    def __init__(self, request):
        self._request = request

    def _get_value(self, getter, key, type_=None):
        try:
            value = getter(key)
            if type_:
                value = type_(value)
            return value
        except KeyError as err:
            raise BadRequest('Should input parameter: {0}'.format(key))
        except (TypeError, ValueError) as err:
            raise BadRequest('Illegal type: {0} ({1})'.format(type_, key))
        assert False

    def _get_matchdict(self, key, *args, **kwds):
        getter = lambda _key: self._request.matchdict[_key]
        return self._get_value(getter, key, *args, **kwds)        

    def _get_params(self, key, *args, **kwds):
        getter = lambda _key: self._request.params[_key]        
        return self._get_value(getter, key, *args, **kwds)

    def get_cooperation_type(self):
        return self._get_params('cooperation_type')
            
    def get_venue(self, organization_id):
        key = 'venue_id'
        venue_id = self._get_matchdict(key)
        try:
            return Venue.query\
                        .join(Venue.organization)\
                        .filter(Organization.id==organization_id)\
                        .filter(Venue.id==venue_id)\
                        .one()
        except NoResultFound as err:
            raise NotFound('Not found venue: {0}={1}'.format(key, venue_id))

