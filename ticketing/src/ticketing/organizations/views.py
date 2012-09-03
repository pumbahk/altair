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
from ..core.models import Organization
from ticketing.organizations.forms import OrganizationForm, SejTenantForm
from ticketing.core.models import Event, Account

from ticketing.sej.models import SejTenant
from ticketing.mails.forms import MailInfoTemplate
from ticketing.models import DBSession
from ticketing.mails.api import get_mail_utility

import logging
logger = logging.getLogger(__name__)

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
        sej_tenants = SejTenant.filter_by(organization_id=organization.id).all()
        return {
            'form':OrganizationForm(),
            'organization':organization,
            'sej_tenants':sej_tenants
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

    ## SEJ Tenant

    @view_config(route_name='organizations.sej_tenant_new', request_method="GET")
    def sej_new(self):
        '''
        '''
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if not organization:
            raise HTTPNotFound()

        form = SejTenantForm()
        return dict(form=form)
    @view_config(route_name='organizations.sej_tenant_new', request_method="POST")
    def sej_new_post(self):
        '''
        '''
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        if not organization:
            raise HTTPNotFound()
        form = SejTenantForm(self.request.POST)
        if not form.validate():
            return dict(form=form)
        else:
            tenant = merge_session_with_post(SejTenant(), form.data)
            tenant.organization = organization
            organization.save()

    @view_config(route_name='organizations.sej_tenant_edit')
    def sej_edit(self):
        '''
        '''
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        sej_tenant_id = int(self.request.matchdict.get('id', 0))
        sej_tenant = SejTenant.get(sej_tenant_id)
        if not organization or not sej_tenant:
            raise HTTPNotFound()
        return dict(sej_tenant=sej_tenant, organization=organization)

    @view_config(route_name='organizations.sej_tenant_edit')
    def sej_edit_post(self):
        '''
        '''
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        organization = Organization.get(organization_id)
        sej_tenant_id = int(self.request.matchdict.get('id', 0))
        sej_tenant = SejTenant.get(sej_tenant_id)
        if not organization or not sej_tenant:
            raise HTTPNotFound()
        form = SejTenantForm(self.request.POST)
        if not form.validate():
            return dict(form=form)
        else:
            tenant = merge_session_with_post(sej_tenant, form.data)
            tenant.organization = organization
            organization.save()

    @view_config(route_name='organizations.sej_tenant_delete')
    def sej_delete(self):
        '''
        '''
        organization_id = int(self.request.matchdict.get('organization_id', 0))
        sej_tenant_id = int(self.request.matchdict.get('id', 0))

@view_defaults(route_name="organizations.mails.new", decorator=with_bootstrap, permission="authenticated", 
               renderer="ticketing:templates/organizations/mailinfo/new.html")
class MailInfoNewView(BaseView):
    @view_config(request_method="GET")
    def mailinfo_new(self):
        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        formclass = MailInfoTemplate(self.request, organization).as_formclass()
        mailtype = self.request.matchdict["mailtype"]
        form = formclass(**(organization.extra_mailinfo.data.get(mailtype, {}) if organization.extra_mailinfo else {}))
        return {"organization": organization, "form": form, "mailtype": mailtype}

    @view_config(request_method="POST")
    def mailinfo_new_post(self):
        logger.debug("mailinfo.post: %s" % self.request.POST)
        mutil = get_mail_utility(self.request, self.request.matchdict["mailtype"])

        organization_id = int(self.request.matchdict.get("organization_id", 0))
        organization = Organization.get(organization_id)
        form = MailInfoTemplate(self.request, organization).as_formclass()(self.request.POST)
        if not form.validate():
            self.request.session.flash(u"入力に誤りがあります。")
            return {"organization": organization, "form": form}
        else:
            mailtype = self.request.matchdict["mailtype"]
            mailinfo = mutil.create_or_update_mailinfo(self.request, form.data, organization=organization, kind=mailtype)
            logger.debug("mailinfo.data: %s" % mailinfo.data)
            DBSession.add(mailinfo)
            self.request.session.flash(u"メールの付加情報を登録しました")
            return HTTPFound(location=route_path('organizations.show', self.request, organization_id=organization.id))

@view_config(route_name="organizations.mails.preview.preorder", 
             decorator=with_bootstrap, permission="authenticated", 
             renderer="string")
def mail_preview_preorder(context, request):
    mutil = get_mail_utility(request, request.matchdict["mailtype"])
    payment_id = request.matchdict["payment_id"]
    delivery_id = request.matchdict["delivery_id"]
    organization_id = int(request.matchdict.get("organization_id", 0))
    organization = Organization.get(organization_id)
    fake_order = mutil.create_fake_order(request, organization, payment_id, delivery_id)
    return mutil.preview_text(request, fake_order)

    
