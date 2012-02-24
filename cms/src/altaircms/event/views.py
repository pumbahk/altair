# coding: utf-8
import json
import collections

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPCreated, HTTPOk
from pyramid.response import Response
from pyramid.view import view_config

from deform import Form
from deform import ValidationFailure

from altaircms.models import DBSession, Event
from altaircms.views import BaseRESTAPI
from altaircms.page.models import Page
from altaircms.event.forms import EventForm
from altaircms.event.mappers import EventMapper, EventsMapper


##
## CMS view
##
@view_config(route_name='event', renderer='altaircms:templates/event/view.mako', permission='view')
def event_view(request):
    id_ = request.matchdict['id']

    event = EventRESTAPIView(request, id_).read()
    pages = DBSession.query(Page).filter_by(event_id=event['id'])

    return dict(
        event=event,
        pages=pages
    )


@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako', permission='view')
def event_list(request):
    events = EventRESTAPIView(request).read()

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.validate():
            request.method = "PUT"
            (created, obj) = EventRESTAPIView(request).create()
            return HTTPFound(request.route_url("event_list"))
    else:
        form = EventForm()
    return dict(
        form=form,
        events=events
    )


##
## API views
##
class EventRESTAPIView(BaseRESTAPI):
    model = Event
    form = EventForm
    object_mapper = EventMapper
    objects_mapper = EventsMapper

    @view_config(route_name='api_event', request_method='PUT')
    def create(self):
        (created, object, errors) = super(EventRESTAPIView, self).create()
        return HTTPCreated() if created else HTTPBadRequest(errors)

    @view_config(route_name='api_event', request_method='GET', renderer='json')
    @view_config(route_name='api_event_object', request_method='GET', renderer='json')
    def read(self):
        resp = super(EventRESTAPIView, self).read()
        if isinstance(resp, collections.Iterable):
            return self.objects_mapper({'events': resp}).as_dict()
        else:
            return self.object_mapper(resp).as_dict()

    @view_config(route_name='api_event_object', request_method='PUT')
    def update(self):
        status = super(EventRESTAPIView, self).update()
        return HTTPOk() if status else HTTPBadRequest()

    @view_config(route_name='api_event_object', request_method='DELETE')
    def delete(self):
        status = super(EventRESTAPIView, self).delete()
        return HTTPOk() if status else HTTPBadRequest()
