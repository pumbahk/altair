# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from deform.form import Form,Button
from deform.exception import ValidationFailure

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post, record_to_appstruct
from ticketing.views import BaseView
from ticketing.organizations.models import Organization
from ticketing.organizations.forms import OrganizationForm

#@view_defaults(decorator=with_bootstrap, permission="administrator")
@view_defaults(decorator=with_bootstrap)
class Organizations(BaseView):
    @view_config(route_name='organizations.index', renderer='ticketing:templates/organizations/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Organization.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Organization.filter()
        query = query.order_by(sort + ' ' + direction)

        organizations = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'organizations': organizations
        }

    @view_config(route_name='organizations.show', renderer='ticketing:templates/organizations/show.html')
    def show(self):
        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)
        return {
            'organization' : organization
        }

    @view_config(route_name='organizations.new', request_method="GET", renderer='ticketing:templates/organizations/new.html')
    def new(self):
        f = Form(OrganizationForm(), buttons=(Button(name='submit',title=u'新規'),))
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                organization = merge_session_with_post(Organization(), data)
                organization.save()

                return HTTPFound(location=route_path('organizations.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            return {
                'form':f.render()
            }

    @view_config(route_name='organizations.edit', renderer='ticketing:templates/organizations/edit.html')
    def edit(self):
        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)
        f = Form(OrganizationForm(), buttons=(Button(name='submit',title=u'更新'),))
        if 'submit' in self.request.POST:
            controls = self.request.POST.items()
            try:
                data = f.validate(controls)
                organization = merge_session_with_post(organization, data)
                organization.save()

                return HTTPFound(location=route_path('organizations.index', self.request))
            except ValidationFailure, e:
                return {'form':e.render()}
        else:
            appstruct = record_to_appstruct(organization)
            return {
                'form':f.render(appstruct=appstruct)
            }
