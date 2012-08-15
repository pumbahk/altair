from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPNotFound
from ticketing.core.models import Event
from ticketing.tickets.models import Ticket

class EventBoundTicketsResource(object):
    __name__ = 'events.tickets'

    ## too-bad
    def __init__(self, request):
        self.request = request
        parent = self.request.registry.getUtility(IRootFactory)(self.request)

        if not hasattr(self, "__acl__") and parent and hasattr(parent, "__acl__"):
            self.__acl__ = parent.__acl__
        self.user = parent.user

    @property
    def event_id(self):
        return self.request.matchdict["event_id"]

    @property
    def event(self):
        event = Event.filter_by(organization_id=self.user.organization_id, id=self.event_id).first()
        if event is None:
            raise HTTPNotFound('event id %s is not found' % self.request.matchdict["event_id"])
        return event

    @property
    def tickets(self):
        return Ticket.filter_by(organization_id=self.user.organization_id, event_id=self.event_id)
