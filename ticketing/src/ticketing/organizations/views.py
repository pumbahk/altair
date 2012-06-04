# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from deform.form import Form,Button
from deform.exception import ValidationFailure

from ticketing.fanstatic import with_bootstrap
from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.organizations.models import Organization
from ticketing.organizations.forms import OrganizationForm
from ticketing.events.models import Event, Account

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
            'form':OrganizationForm(),
            'organization':organization,
            'distributing_events':Event.get_distributing(organization_id=organization_id),
            'distributed_events':Event.get_distributed(user_id=organization.user_id),
        }

    @view_config(route_name='organizations.new', request_method='GET', renderer='ticketing:templates/organizations/edit.html')
    def new_get(self):
        return {
            'form':OrganizationForm(),
        }

    @view_config(route_name='organizations.new', request_method='POST', renderer='ticketing:templates/organizations/edit.html')
    def new_post(self):
        f = OrganizationForm(self.request.POST)

        if f.validate():
            organization = merge_session_with_post(Organization(), f.data)
            organization.user_id = 1
            organization.save()

            self.request.session.flash(u'配券先／配券元を保存しました')
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization.id))
        else:
            return {
                'form':f,
            }

    @view_config(route_name='organizations.edit', request_method='GET', renderer='ticketing:templates/organizations/edit.html')
    def edit_get(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)

        f = OrganizationForm()
        f.process(record_to_multidict(organization))
        return {
            'form':f,
        }

    @view_config(route_name='organizations.edit', request_method='POST', renderer='ticketing:templates/organizations/edit.html')
    def edit_post(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)

        f = OrganizationForm(self.request.POST)
        if f.validate():
            organization = merge_session_with_post(organization, f.data)
            organization.save()

            self.request.session.flash(u'配券先／配券元を保存しました')
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization.id))
        else:
            return {
                'form':f,
            }

    @view_config(route_name='organizations.delete')
    def delete(self):
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if organization is None:
            return HTTPNotFound("organization id %d is not found" % organization_id)

        organization.delete()

        self.request.session.flash(u'配券先／配券元を削除しました')
        return HTTPFound(location=route_path('organizations.index', self.request))
