# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post, record_to_appstruct, merge_and_flush, record_to_multidict
from ticketing.organizations.forms import OrganizationForm
from ..core.models import Organization
from ticketing.operators.models import Operator, OperatorRole, Permission
from ticketing.operators.forms import OperatorForm, OperatorRoleForm
from deform.form import Form,Button
from deform.exception import ValidationFailure

import  sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class Operators(BaseView):

    def _role_id_list_to_role_list(self, role_id_list):
        return [session.query(OperatorRole).filter(OperatorRole.id==role_id).one() for role_id in role_id_list]

    @view_config(route_name='operators.index', renderer='ticketing:templates/operators/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Operator.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Operator.filter_by(organization_id=self.context.user.organization_id).order_by(sort + ' ' + direction)

        operators = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'operators': operators
        }

    @view_config(route_name='operators.show', renderer='ticketing:templates/operators/show.html')
    def show(self):
        operator_id = int(self.request.matchdict.get('operator_id', 0))
        operator = Operator.get(operator_id)
        if operator is None:
            return HTTPNotFound("operator_id %d is not found" % operator_id)

        return {
            'form':OperatorForm(),
            'form_organization':OrganizationForm(),
            'operator':operator,
        }

    @view_config(route_name='operators.new', request_method='GET', renderer='ticketing:templates/operators/edit.html')
    def new_get(self):
        return {
            'form':OperatorForm(organization_id=self.context.user.organization_id),
        }

    @view_config(route_name='operators.new', request_method='POST', renderer='ticketing:templates/operators/edit.html')
    def new_post(self):
        f = OperatorForm(self.request.POST)
        if f.validate():
            #operator = merge_session_with_post(Operator(), f.data, filters={'roles':self._role_id_list_to_role_list()})
            operator = merge_session_with_post(Operator(), f.data)
            operator.expire_at = datetime.today() + timedelta(days=180)
            operator.role_ids = f.data['role_ids']
            operator.save()

            self.request.session.flash(u'オペレーターを保存しました')
            return HTTPFound(location=route_path('operators.show', self.request, operator_id=operator.id))
        else:
            return {
                'form':f
            }

    @view_config(route_name='operators.edit', request_method='GET', renderer='ticketing:templates/operators/edit.html')
    def edit_get(self):
        operator_id = int(self.request.matchdict.get('operator_id', 0))
        operator = Operator.get(operator_id)
        if operator is None:
            return HTTPNotFound("Operator id %d is not found" % operator_id)

        f = OperatorForm(obj=operator)
        return {
            'form':f,
        }

    @view_config(route_name='operators.edit', request_method='POST', renderer='ticketing:templates/operators/edit.html')
    def edit_post(self):
        operator_id = int(self.request.matchdict.get('operator_id', 0))
        operator = Operator.get(operator_id)
        if operator is None:
            return HTTPNotFound("Operator id %d is not found" % operator_id)

        f = OperatorForm(self.request.POST)
        f.password.data = operator.auth.password
        f.expire_at.data = operator.expire_at
        if f.validate():
            #operator = merge_session_with_post(operator, f.data, filters={'roles':self._role_id_list_to_role_list()})
            operator = merge_session_with_post(operator, f.data)
            operator.role_ids = f.data['role_ids']
            operator.save()

            self.request.session.flash(u'オペレーターを保存しました')
            return HTTPFound(location=route_path('operators.show', self.request, operator_id=operator.id))
        else:
            return {
                'form':f,
            }

    @view_config(route_name='operators.delete')
    def delete(self):
        operator_id = int(self.request.matchdict.get('operator_id', 0))
        operator = Operator.get(operator_id)
        if operator is None:
            return HTTPNotFound("Operator id %d is not found" % operator_id)

        operator.delete()

        self.request.session.flash(u'オペレーターを削除しました')
        return HTTPFound(location=route_path('operators.index', self.request))

@view_defaults(decorator=with_bootstrap, permission='administrator')
class OperatorRoles(BaseView):

    @view_config(route_name='operator_roles.index', renderer='ticketing:templates/operator_roles/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'OperatorRole.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = session.query(OperatorRole).order_by(sort + ' ' + direction)

        roles = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'roles':roles
        }

    @view_config(route_name='operator_roles.new', renderer='ticketing:templates/operator_roles/edit.html')
    def new(self):
        f = Form(OperatorRoleForm(), buttons=(Button(name='submit',title=u'新規'),))
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                record = OperatorRole()
                record = merge_session_with_post(record, data)
                session.add(record)
                return HTTPFound(location=route_path('operator_roles.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            return {
                'form':f.render()
            }

    @view_config(route_name='operator_roles.edit', renderer='ticketing:templates/operator_roles/edit.html')
    def edit(self):
        operator_id = int(self.request.matchdict.get("operator_id", 0))
        operator = session.query(OperatorRole).filter(OperatorRole.id == operator_id)
        if operator is None:
            return HTTPNotFound("Operator id %d is not found" % operator_id)

        f = OperatorRoleForm()
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                record = merge_session_with_post(operator, data)
                merge_and_flush(record)

                return HTTPFound(location=route_path('operator_roles.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            return {
                'form':f
            }

@view_defaults(decorator=with_bootstrap, permission="master_editor")
class Permissions(BaseView):

    @view_config(route_name='permissions.index', renderer='ticketing:templates/permissions/index.html')
    def index(self):
        return {}
