# coding: utf-8
from Carbon import Res
import isodate
import json
import collections

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPCreated, HTTPOk
from pyramid.response import Response
from pyramid.view import view_config
import transaction

from altaircms.models import DBSession, Event, Performance, Sale, Ticket
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
def parse_and_save_event(jsonstring):
    parsed = json.loads(jsonstring)

    try:
        for event in parsed['events']:
            event_obj = Event()
            event_obj.backend_event_id = event['id']
            event_obj.name = event['name']
            event_obj.event_on = isodate.parse_datetime(event['start_on'])
            event_obj.event_close = isodate.parse_datetime(event['end_on'])
            DBSession.add(event_obj)
            event_obj = DBSession.merge(event_obj)

            if 'performances' in event:
                for performance in event['performances']:
                    performance_obj = Performance()
                    performance_obj.event_id = event_obj.id
                    performance_obj.backend_performance_id = performance['id']
                    performance_obj.title = performance['name']
                    performance_obj.place = performance['venue']
                    performance_obj.open_on = isodate.parse_datetime(performance['open_on'])
                    performance_obj.start_on = isodate.parse_datetime(performance['start_on'])
                    # performance_obj.end_on = isodate.parse_datetime(performance['end_on'])  # TODO: end_onの必須有無確認
                    performance_obj.end_on = isodate.parse_datetime(performance['end_on']) if 'end_on' in performance else None
                    DBSession.add(performance_obj)
                    performance_obj = DBSession.merge(performance_obj)

                    if 'sales' in performance:
                        for sale in performance['sales']:
                            sale_obj = Sale()
                            sale_obj.performance_id = performance_obj.id
                            sale_obj.name = sale['name']
                            sale_obj.start_on = isodate.parse_datetime(sale['start_on'])
                            sale_obj.end_on = isodate.parse_datetime(sale['end_on'])
                            DBSession.add(sale_obj)
                            sale_obj = DBSession.merge(sale_obj)

                            if 'tickets' in sale:
                                for ticket in sale['tickets']:
                                    ticket_obj = Ticket()
                                    ticket_obj.sale_id = sale_obj.id
                                    ticket_obj.name = ticket['name']
                                    ticket_obj.price = ticket['price']
                                    ticket_obj.seat_type = ticket['seat_type']
                                    DBSession.add(ticket_obj)
                                    ticket_obj = DBSession.merge(ticket_obj)
    except:
        raise

    transaction.commit()

    return True


@view_config(route_name="api_event_register", request_method="POST", renderer="json")
def event_register(request):
    form = EventRegisterForm(request.POST)
    if form.validate():
        try:
            parse_and_save_event(request.POST['jsonstring'])
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
