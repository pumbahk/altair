# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Account, Event
from ticketing.accounts.forms import AccountForm
from ticketing.organizations.forms import OrganizationForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Accounts(BaseView):

    @view_config(route_name='accounts.index', renderer='ticketing:templates/accounts/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Account.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Account.filter_by(organization_id=int(self.context.user.organization_id)).order_by(sort + ' ' + direction)
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

    @view_config(route_name='accounts.show', renderer='ticketing:templates/accounts/show.html')
    def show(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.get(account_id)
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        return {
            'form':AccountForm(record_to_multidict(account)),
            'form_organization':OrganizationForm(),
            'account':account,
            'owner_events':Event.get_owner_event(user_id=account.user.id),
            'client_events':Event.get_client_event(user_id=account.user.id),
        }

    @view_config(route_name='accounts.new', request_method='POST', renderer='ticketing:templates/accounts/_form.html')
    def new_post(self):
        f = AccountForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            account = merge_session_with_post(Account(), f.data)
            account.organization_id = self.context.user.organization.id
            account.save()

            self.request.session.flash(u'取引先を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='accounts.edit', request_method='POST', renderer='ticketing:templates/accounts/_form.html')
    def edit_post(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.get(account_id)
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        f = AccountForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            account = merge_session_with_post(account, f.data)
            account.organization_id = self.context.user.organization.id
            account.save()

            self.request.session.flash(u'取引先を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='accounts.delete')
    def delete(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.get(account_id)
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
