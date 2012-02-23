# coding: utf-8
import json

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config

from deform import Form
from deform import ValidationFailure

from altaircms.event.forms import event_schema
from altaircms.models import DBSession, Event
from altaircms.views import BaseRESTAPIView
from altaircms.page.models import Page
from altaircms.event.forms import EventForm


##
## CMS view
##

@view_config(route_name='event', renderer='altaircms:templates/event/view.mako')
def event_view(request):
    id_ = request.matchdict['id']

    event = DBSession.query(Event).get(id_)
    pages = DBSession.query(Page).filter_by(event_id=event.id)

    return dict(
        event=event,
        pages=pages
    )


@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako')
def event_list(request):
    events = DBSession.query(Event).order_by(Event.id.desc()).all()
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
class EventRESTAPIView(BaseRESTAPIView):
    model = Event
    form = EventForm

    @view_config(route_name='api_event', request_method='PUT', renderer='json')
    @view_config(route_name='api_event', request_method='PUT', request_param="html=t", renderer='altaircms:templates/event/parts/form.mako')
    def create(self):
        return super(EventRESTAPIView, self).create()

    @view_config(route_name='api_event', request_method='GET')
    @view_config(route_name='api_event_object', request_method='GET')
    def read(self):
        return super(EventRESTAPIView, self).read()

    @view_config(route_name='api_event_object', request_method='PUT')
    def update(self):
        return super(EventRESTAPIView, self).update()

    @view_config(route_name='api_event_object', request_method='DELETE')
    def delete(self):
        return super(EventRESTAPIView, self).delete()


'''
@view_config(route_name='api_event_list', request_method='GET')
def list(reuqest):
    """
    イベントの一覧ビュー

    @TODO: 認証を加える
    """
    events = DBSession.query(Event).order_by(Event.id.desc()).all()

    output = []
    for event in events:
        # @TODO: 何かしらのマッピングライブラリを使う（bpmappers?）
        dist = {
            'id':event.id,
            'title':event.title,
            'description':event.description
        }
        output.append(dist)
    res = json.dumps(output)

    return Response(res, content_type='application/json')


@view_config(route_name='api_event_list', request_method='PUT')
def put(request):
    """
    イベントオブジェクト追加
    """
    myform = Form(event_schema, buttons=('submit',), use_ajax=True)

    try:
        controls = request.POST.items()
        appstruct = myform.validate(controls)
    except ValidationFailure, e:
        return Response(json.dumps(e.error.asdict()), content_type='application/json', status=400)

    model = Event(title=appstruct['title'],subtitle=appstruct['subtitle'], description=appstruct['description'])
    DBSession.add(model)

    return Response('', status=201)


@view_config(route_name='api_event', request_method='GET')
def get(request):
    """
    イベントオブジェクトの取得
    """
    id_ = request.matchdict['id']

    dbsession = DBSession()
    event = dbsession.query(Event).get(id_)
    DBSession.remove()

    res = {
        'id': event.id,
        'title': event.title,
        'description': event.description
    }

    return Response(json.dumps(res), content_type='application/json')

@view_config(route_name='api_event', request_method='DELETE')
def delete(request):
    """
    イベントオブジェクトの削除
    """
    id_ = request.matchdict['id']

    dbsession = DBSession()
    event = dbsession.query(Event).get(id_)
    dbsession.delete(event)
    DBSession.remove()

    return Response('')


@view_config(route_name='api_event', request_method='PUT')
def post(request):
    """
    イベントオブジェクトの更新
    """
    id_ = request.matchdict['id']

    dbsession = DBSession()
    event = dbsession.query(Event).get(id_)

    event.title = appstruct['title']
    event.subtitle = appstruct['subtitle']
    event.description = appstruct['description']

    dbsession.add(event)
    DBSession.remove()

    return Response('')
'''
