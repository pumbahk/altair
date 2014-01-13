#-*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implementer
from sqlalchemy.orm.exc import NoResultFound
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    )
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event,
    )


class _RequestAccessor(object):
    in_params = ()
    in_matchdict = ()
    
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
        getter = lambda _key: self._request.params.getall(_key)
        return self._get_value(getter, key, *args, **kwds)

    def __getattr__(self, name):
        if name in self.in_params:
            return self._get_params(name)
        elif name in self.in_matchdict:
            return self._get_matchdict(name)
        else:
            raise AttributeError(name)

class CooperationRequestAccessor(_RequestAccessor):
    in_params = ()
    in_matchdict = ('event_id',)
    

class ICooperationResource(Interface):
    pass

@implementer(ICooperationResource)
class CooperationEventResource(TicketingAdminResource):
    accessor_factory = CooperationRequestAccessor
    
    def __init__(self, request):
        super(CooperationEventResource, self).__init__(request)        
        accessor = self.accessor_factory(request)
        
        event_id = accessor.event_id
        try:
            self.event = Event.query.filter(Event.id==event_id).one()
        except NoResultFound:
            return HTTPNotFound('event_id={}'.format(event_id))
