# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime, timedelta
from paste.util.multidict import MultiDict

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import DBSession, merge_session_with_post
from altair.app.ticketing.organizations.forms import OrganizationForm
from altair.app.ticketing.core.models import Organization
from altair.app.ticketing.operators.models import Operator, OperatorRole, Permission
from altair.app.ticketing.operators.forms import OperatorForm, OperatorRoleForm

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class Operators(BaseView):

    @view_config(route_name='operators.index', renderer='altair.app.ticketing:templates/operators/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Operator.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Operator.query.filter_by(organization_id=self.context.organization.id).order_by(sort + ' ' + direction)

        operators = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
            )

        return {
            'operators': operators
            }

    @view_config(route_name='operators.show', renderer='altair.app.ticketing:templates/operators/show.html')
    def show(self):
        return {
            'form':OperatorForm(organization_id=self.context.organization.id),
            'form_organization':OrganizationForm(),
            'operator':self.context.operator,
            }

    @view_config(route_name='operators.new', request_method='GET', renderer='altair.app.ticketing:templates/operators/edit.html')
    def new_get(self):
        return {
            'form':OperatorForm(organization_id=self.context.organization.id),
            }

    @view_config(route_name='operators.new', request_method='POST', renderer='altair.app.ticketing:templates/operators/edit.html')
    def new_post(self):
        f = OperatorForm(self.request.POST, organization_id=self.context.organization.id)
        if f.validate():
            operator = merge_session_with_post(Operator(), f.data)
            operator.expire_at = datetime.today() + timedelta(days=180)
            operator.role_ids = f.data['role_ids']
            operator.save()

            self.request.session.flash(u'オペレーターを保存しました')
            return HTTPFound(location=route_path('operators.show', self.request, operator_id=operator.id))
        else:
            return {
                'form': f,
                }

    @view_config(route_name='operators.edit', request_method='GET', renderer='altair.app.ticketing:templates/operators/edit.html')
    def edit_get(self):
        f = OperatorForm(obj=self.context.operator, organization_id=self.context.organization.id)
        try:
            f.validate_id(f.id)
        except Exception, e:
            self.request.session.flash(e.message)
            return HTTPFound(location=route_path('operators.show', self.request, operator_id=self.context.operator_id))

        return {
            'form':f,
            }

    @view_config(route_name='operators.edit', request_method='POST', renderer='altair.app.ticketing:templates/operators/edit.html')
    def edit_post(self):
        operator = self.context.operator

        f = OperatorForm(self.request.POST, organization_id=self.context.organization.id)
        f.password.data = operator.auth.password
        f.expire_at.data = operator.expire_at
        if f.validate():
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
        operator = self.context.operator

        f = OperatorForm(obj=operator, organization_id=self.context.organization.id)
        try:
            f.validate_id(f.id)
        except Exception, e:
            self.request.session.flash(e.message)
            return HTTPFound(location=route_path('operators.show', self.request, operator_id=operator.id))

        operator.delete()
        self.request.session.flash(u'オペレーターを削除しました')
        return HTTPFound(location=route_path('operators.index', self.request))

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class OperatorRoles(BaseView):

    @view_config(route_name='operator_roles.index', renderer='altair.app.ticketing:templates/operator_roles/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'OperatorRole.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = OperatorRole.query_all(organization_id=self.context.organization.id).order_by(sort + ' ' + direction)
        roles = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=10,
            url=paginate.PageURL_WebOb(self.request)
            )

        return {
            'roles':roles,
            }

    @view_config(route_name='operator_roles.new', request_method='GET', renderer='altair.app.ticketing:templates/operator_roles/edit.html')
    def new_get(self):
        return {
            'form':OperatorRoleForm(organization_id=self.context.organization.id),
            }

    @view_config(route_name='operator_roles.new', request_method='POST', renderer='altair.app.ticketing:templates/operator_roles/edit.html')
    def new_post(self):
        f = OperatorRoleForm(self.request.POST, organization_id=self.context.organization.id)
        if f.validate():
            operator_role = merge_session_with_post(OperatorRole(), f.data)
            permissions = []
            for p in f.permissions.data:
                permissions.append(Permission(category_name=p, permit=1))
            operator_role.permissions = permissions
            operator_role.save()

            self.request.session.flash(u'ロールを保存しました')
            return HTTPFound(location=route_path('operator_roles.index', self.request))
        else:
            return {
                'form':f,
                }

    @view_config(route_name='operator_roles.edit', request_method='GET', renderer='altair.app.ticketing:templates/operator_roles/edit.html')
    def edit_get(self):
        return {
            'form':OperatorRoleForm(obj=self.context.operator_role),
            }

    @view_config(route_name='operator_roles.edit', request_method='POST', renderer='altair.app.ticketing:templates/operator_roles/edit.html')
    def edit_post(self):
        operator_role = self.context.operator_role

        f = OperatorRoleForm(self.request.POST, organization_id=self.context.organization.id)
        if f.validate():
            operator_role = merge_session_with_post(operator_role, f.data)
            permissions = []
            for p in operator_role.permissions:
                if p.category_name not in f.permissions.data:
                    DBSession.delete(p)
                else:
                    permissions.append(p.category_name)
            for p in f.permissions.data:
                if p not in permissions:
                    operator_role.permissions.append(Permission(category_name=p, permit=1))
            operator_role.save()

            self.request.session.flash(u'ロールを保存しました')
            return HTTPFound(location=route_path('operator_roles.index', self.request))
        else:
            return {
                'form':f,
                }

    @view_config(route_name='operator_roles.delete')
    def delete(self):
        operator_role = self.context.operator_role

        f = OperatorRoleForm(obj=operator_role)
        try:
            if f.validate_id(f.id):
                DBSession.delete(operator_role)
                self.request.session.flash(u'ロールを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)

        return HTTPFound(location=route_path('operator_roles.index', self.request))

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class Permissions(BaseView):

    @view_config(route_name='permissions.index', renderer='altair.app.ticketing:templates/permissions/index.html')
    def index(self):
        return {}
