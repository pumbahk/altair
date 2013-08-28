# -*- coding: utf-8 -*-

import logging
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.models import merge_session_with_post, record_to_multidict
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Account, Event
from altair.app.ticketing.sej.models import SejTenant
from .forms import AccountForm
from altair.app.ticketing.organizations.forms import OrganizationForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='master_editor')
class Accounts(BaseView):

    @view_config(route_name='accounts.index', renderer='altair.app.ticketing:templates/accounts/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Account.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Account.query.filter_by(organization_id=self.context.user.organization_id).order_by(sort + ' ' + direction)
        accounts = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':AccountForm(),
            'accounts':accounts,
        }

    @view_config(route_name='accounts.show', renderer='altair.app.ticketing:templates/accounts/show.html')
    def show(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.query.filter_by(id=account_id).filter_by(organization_id=self.context.user.organization_id).first()
        if account is None or account.user is None:
            return HTTPNotFound('account id %d not found' % account_id)

        return {
            'form':AccountForm(record_to_multidict(account)),
            'form_organization':OrganizationForm(),
            'account':account,
            'owner_events':Event.get_owner_event(account),
            'client_events':Event.get_client_event(account),
            'sej_tenants':SejTenant.filter_by(organization_id=account.user.organization.id).all()
        }

    @view_config(route_name='accounts.new', request_method='GET', renderer='altair.app.ticketing:templates/accounts/_form.html', xhr=True)
    def new(self):
        f = AccountForm()
        return {
            'form':f,
            'action': self.request.path,
        }

    @view_config(route_name='accounts.new', request_method='POST', renderer='altair.app.ticketing:templates/accounts/_form.html', xhr=True)
    def new_post(self):
        f = AccountForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            account = Account(
                account_type=f.data['account_type'],
                user_id=f.data['user_id'],
                name=f.data['name'],
                organization_id = self.context.user.organization.id
                )
            account.save()

            self.request.session.flash(u'取引先を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path,
            }

    @view_config(route_name='accounts.edit', request_method='GET', renderer='altair.app.ticketing:templates/accounts/_form.html', xhr=True)
    def edit(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.query.filter_by(id=account_id).filter_by(organization_id=self.context.user.organization_id).first()
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        f = AccountForm(obj=account)
        return {
            'form':f,
            'action': self.request.path,
        }

    @view_config(route_name='accounts.edit', request_method='POST', renderer='altair.app.ticketing:templates/accounts/_form.html', xhr=True)
    def edit_post(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.query.filter_by(id=account_id).filter_by(organization_id=self.context.user.organization_id).first()
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        f = AccountForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            account = merge_session_with_post(account, f.data)
            account.organization_id = self.context.user.organization.id
            account.save()

            self.request.session.flash(u'取引先を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path,
            }

    @view_config(route_name='accounts.delete')
    def delete(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.query.filter_by(id=account_id).filter_by(organization_id=self.context.user.organization_id).first()
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        location = route_path('accounts.index', self.request)
        try:
            account.delete()
            self.request.session.flash(u'取引先を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
