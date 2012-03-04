# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, session
from ticketing.models.boxoffice import OperatorRole

from forms import OperatorRoleForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

import webhelpers.paginate as paginate

@view_config(route_name='admin.operator_roles.index', renderer='ticketing:templates/operator_roles/index.html')
def index(context, request):
    current_page = int(request.params.get("page", 0))
    page_url = paginate.PageURL_WebOb(request)
    query = session.query(OperatorRole)
    roles = paginate.Page(query.order_by(OperatorRole.id), current_page, url=page_url)
    return {
        'roles': roles
    }

@view_config(route_name='admin.operator_roles.new', renderer='ticketing:templates/operator_roles/new.html')
def new(context, request):
    f = Form(OperatorRoleForm(), buttons=(Button(name='submit',title=u'新規'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            data = f.validate(controls)
            record = OperatorRole()
            record = merge_session_with_post(record, data)
            session.add(record)
            return HTTPFound(location=route_path('admin.operator_roles.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        return {
            'form':f.render()
        }
    
@view_config(route_name='admin.operator_roles.edit', renderer='ticketing:templates/operator_roles/edit.html')
def edit(context, request):
    operator_id = int(request.matchdict.get("operator_id", 0))
    operator = session.query(OperatorRole).filter(OperatorRole.id == operator_id)
    if operator is None:
        return HTTPNotFound("Operator id %d is not found" % operator_id)
    f = Form(OperatorRoleForm(), buttons=(Button(name='submit',title=u'更新'),))
    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            
            data = f.validate(controls)
            record = merge_session_with_post(operator, data)
            merge_and_flush(record)

            return HTTPFound(location=route_path('admin.operator_roles.index', request))
        except ValidationFailure, e:
            return {'form':e.render()}
    else:
        appstruct = record_to_appstruct(operator)
        return {
            'form':f.render(appstruct=appstruct)
        }