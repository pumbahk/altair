# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct
from ticketing.models.boxoffice import Client

from forms import ClientForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

import webhelpers.paginate as paginate

@view_config(route_name='admin.clients.index', renderer='ticketing:templates/clients/index.html')
def index(context, request):
    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)
    query = Client.query()
    clients = paginate.Page(query.order_by(Client.id), current_page, url=page_url)
    return {
        'clients': clients
    }


@view_config(route_name='admin.clients.show', renderer='ticketing:templates/clients/show.html')
def show(context, request):
    client_id = int(request.matchdict.get("client_id", 0))
    client = Client.get(client_id)
    if client is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    return {
        'client' : client
    }

@view_config(route_name='admin.clients.new', renderer='ticketing:templates/clients/new.html')
def new(context, request):
    f = Form(ClientForm(), buttons=(Button(name='submit',title=u'新規'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = Client()
            record = merge_session_with_post(record, controls)
            Client.add(record)
            return HTTPFound(location=route_path('admin.client.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        return {
            'form':f.render()
        }

@view_config(route_name='admin.clients.edit', renderer='ticketing:templates/clients/edit.html')
def edit(context, request):
    client_id = int(request.matchdict.get("client_id", 0))
    client = Client.get(client_id)
    if client is None:
        return HTTPNotFound("client id %d is not found" % client_id)
    f = Form(ClientForm(), buttons=(Button(name='submit',title=u'更新'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = merge_session_with_post(client, controls)
            Client.update(record)
            return HTTPFound(location=route_path('admin.clients.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        appstruct = record_to_appstruct(client)
        return {
            'form':f.render(appstruct=appstruct)
        }
