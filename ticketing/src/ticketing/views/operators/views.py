# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, session
from ticketing.models.boxoffice import Operator, OperatorRole, Client

from forms import OperatorForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from hashlib import md5

import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap)
class Operator(BaseView):

    def _role_id_list_to_role_list(self, role_id_list):
        return [ session.query(OperatorRole).filter(OperatorRole.id==role_id).one() for role_id in role_id_list]

    @view_config(route_name='operators.index', renderer='ticketing:templates/operators/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Operator)
        operators = paginate.Page(query.order_by(Operator.id), current_page, url=page_url)
        return {
            'operators': operators
        }

    @view_config(route_name='operators.new', renderer='ticketing:templates/operators/new.html')
    def new(self):

        form = OperatorForm(self.request.POST)
        if 'submit' in self.request.POST:
            if form.validate():
                record = Operator()
                record = merge_session_with_post(record, data, filters={'roles' : _role_id_list_to_role_list})
                record.secret_key = md5(record.secret_key).hexdigest()
                print data
                session.add(record)
                return HTTPFound(location=route_path('admin.operators.index', request))

        else:
            return {
                'form':f.render()
            }

    @view_config(route_name='operators.edit', renderer='ticketing:templates/operators/edit.html')
    def edit(context, request):
        operator_id = int(request.matchdict.get("operator_id", 0))
        operator = session.query(Operator).filter(Operator.id == operator_id)
        if operator is None:
            return HTTPNotFound("Operator id %d is not found" % operator_id)
        f = Form(
            OperatorForm().bind(
                role_choices=[(role.id, role.name) for role in session.query(OperatorRole).all()],
                client_choices=[(client.id, client.name) for client in session.query(Client).all()]
            ),
            buttons=(Button(name='submit',title=u'更新'),)
        )
        if 'submit' in request.POST:
            controls = request.POST.items()
            try:
                data = f.validate(controls)
                record = merge_session_with_post(operator, data, filters={'roles' : _role_id_list_to_role_list})
                record.secret_key = md5(record.secret_key).hexdigest()
                merge_and_flush(record)

                return HTTPFound(location=route_path('admin.operators.index', request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            appstruct = record_to_appstruct(operator)
            return {
                'form':f.render(appstruct=appstruct)
            }

    @view_config(route_name='operators.show', renderer='ticketing:templates/operators/show.html')
    def show(context, request):
        operator_id = int(request.matchdict.get("operator_id", 0))
        operator = session.query(Operator).filter(Operator.id == operator_id).one()
        if operator is None:
            return HTTPNotFound("operator_id %d is not found" % operator_id)
        return {
            'operator' : operator
        }