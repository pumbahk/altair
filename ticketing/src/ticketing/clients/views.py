# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct
from .models import Client, session
from ticketing.views import BaseView

from forms import ClientForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

import webhelpers.paginate as paginate
from ticketing.fanstatic import with_bootstrap

#@view_defaults(decorator=with_bootstrap, permission="administrator")
@view_defaults(decorator=with_bootstrap)
class Clients(BaseView):
    @view_config(route_name='clients.index', renderer='ticketing:templates/clients/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Client)
        clients = paginate.Page(query.order_by(Client.id), current_page, url=page_url)
        return {
            'clients': clients
        }


    @view_config(route_name='clients.show', renderer='ticketing:templates/clients/show.html')
    def show(self):
        client_id = int(self.request.matchdict.get("client_id", 0))
        client = Client.get(client_id)
        if client is None:
            return HTTPNotFound("client id %d is not found" % client_id)
        return {
            'client' : client
        }

    @view_config(route_name='clients.new', request_method="GET", renderer='ticketing:templates/clients/new.html')
    def new(self):
        f = Form(ClientForm(), buttons=(Button(name='submit',title=u'新規'),))
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                record = Client()
                record = merge_session_with_post(record, data)
                Client.add(record)
                return HTTPFound(location=route_path('clients.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            return {
                'form':f.render()
            }

    @view_config(route_name='clients.edit', renderer='ticketing:templates/clients/edit.html')
    def edit(self):
        client_id = int(self.request.matchdict.get("client_id", 0))
        client = Client.get(client_id)
        if client is None:
            return HTTPNotFound("client id %d is not found" % client_id)
        f = Form(ClientForm(), buttons=(Button(name='submit',title=u'更新'),))
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                record = merge_session_with_post(client, data)
                Client.update(record)
                return HTTPFound(location=route_path('clients.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            appstruct = record_to_appstruct(client)
            return {
                'form':f.render(appstruct=appstruct)
            }
