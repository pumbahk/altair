# coding: utf-8
import json

from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.view import view_config

from deform import Form
from deform import ValidationFailure

from altaircms.event.forms import event_schema
from altaircms.models import DBSession, Event, Page


##
## CMS view
##
@view_config(route_name='event', renderer='altaircms:templates/event/view.mako')
def event_view(request):
    id_ = request.matchdict['id']

    dbsession = DBSession()
    event = dbsession.query(Event).get(id_)
    pages = dbsession.query(Page).filter_by(event_id=event.id)
    DBSession.remove()

    return dict(
        event=event,
        pages=pages
    )


@view_config(route_name='event_list', renderer='altaircms:templates/event/list.mako')
def event_list(request):
    dbsession = DBSession()
    events = dbsession.query(Event).order_by(Event.id.desc()).all()
    DBSession.remove()

    return dict(
        events=events
    )


##
## API views
##
@view_config(route_name='api_event_list', request_method='GET')
def list(reuqest):
    """
    イベントの一覧ビュー

    @TODO: 認証を加える
    """
    dbsession = DBSession()
    events = dbsession.query(Event).order_by(Event.id.desc()).all()
    DBSession.remove()

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
    dbsession = DBSession()
    dbsession.add(model)
    DBSession.remove()

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

    event.title=appstruct['title']
    event.subtitle=appstruct['subtitle']
    event.description=appstruct['description']

    dbsession.add(event)
    DBSession.remove()

    return Response('')