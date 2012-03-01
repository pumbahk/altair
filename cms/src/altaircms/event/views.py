# coding: utf-8
from Carbon import Res
import json
import collections

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPCreated, HTTPOk
from pyramid.response import Response
from pyramid.view import view_config

from altaircms.models import DBSession, Event, Performance
from altaircms.views import BaseRESTAPI
from altaircms.page.models import Page
from altaircms.fanstatic import with_bootstrap

from altaircms.event.forms import EventForm, EventRegisterForm
from altaircms.event.mappers import EventMapper, EventsMapper


##
## CMS view
##
@view_config(route_name='event', renderer='altaircms:templates/event/view.mako', permission='event_read',
             decorator=with_bootstrap)
def view(request):
    id_ = request.matchdict['id']

    event = EventRESTAPIView(request, id_).read()
    pages = DBSession.query(Page).filter_by(event_id=event['id'])

    return dict(
        event=event,
        pages=pages
    )


@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako', permission='event_create', request_method="POST", 
             decorator=with_bootstrap)
@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako', permission='event_read', request_method="GET", 
             decorator=with_bootstrap)
def list_(request):
    events = EventRESTAPIView(request).read()

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.validate():
            request.method = "PUT"
            EventRESTAPIView(request).create()
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


##
## バックエンドとの通信用
##
def parse_eventdata(jsonstring):
    parsed = json.loads(jsonstring)
    for event in parsed['events']:
        event_obj = Event()
        event_obj.backend_event_id = event['id']
        event_obj.name = event['name']
        event_obj.event_on = event['start_on']
        event_obj.event_close = event['end_on']

        DBSession.add(event_obj)

        if 'performances' in event:
            for performance in event['performances']:
                performance_obj = Performance()
                performance_obj.backend_performance_id = performance['id']
                performance_obj.backend_performance_id = performance['id']
                performance_obj.title = performance['name']
                performance_obj.place = performance['venue']
                performance_obj.open_on = performance['open_on']
                performance_obj.start_on = performance['start_on']
                performance_obj.end_on = performance['end_on']

                if 'sales' in performance:
                    for sale in performance['sales']:



                        if 'tickets' in sale:
                            pass

@view_config(route_name="api_event_register", request_method="POST", renderer="json")
def event_register(request):
    form = EventRegisterForm(request.POST)
    if form.validate():
        try:
            parse_eventdata(request.POST['jsonstring'])
        except Exception as e:
            return Response(json.dumps({
                'error':str(e)
            }), status=400, content_type='text/plain')
        return HTTPCreated()
    else:
        return Response(
            json.dumps(form.errors),
            content_type='application/json',
            status=400
        )
