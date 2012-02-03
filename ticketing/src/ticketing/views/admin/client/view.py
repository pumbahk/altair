# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path


from ticketing.models import merge_session_with_post, record_to_appstruct
from ticketing.models.boxoffice import Client
from ticketing.models.event import *
from forms import ClientForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

@view_config(route_name='admin.client.index', renderer='ticketing:templates/client/index.html')
def index(context, request):
    return {
        'clients' : client_all_list()
    }

@view_config(route_name='admin.client.show', renderer='ticketing:templates/client/show.html')
def show(context, request):
    client_id = int(request.matchdict.get("client_id", 0))
    client = client_get(client_id)
    if client is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    return {
        'client' : client
    }

@view_config(route_name='admin.client.new', renderer='ticketing:templates/client/new.html')
def new(context, request):
    f = Form(ClientForm(), buttons=(Button(name='submit',title=u'新規'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = Client()
            record = merge_session_with_post(record, controls)
            client_add(record)
            return HTTPFound(location=route_path('admin.client.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        return {
            'form':f.render()
        }

@view_config(route_name='admin.client.edit', renderer='ticketing:templates/client/edit.html')
def edit(context, request):
    client_id = int(request.matchdict.get("client_id", 0))
    client = client_get(client_id)
    if client is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    f = Form(ClientForm(), buttons=(Button(name='submit',title=u'更新'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = merge_session_with_post(client, controls)
            client_update(record)
            return HTTPFound(location=route_path('admin.client.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        appstruct = record_to_appstruct(client)
        return {
            'form':f.render(appstruct=appstruct)
        }
