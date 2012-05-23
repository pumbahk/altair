# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.models import merge_session_with_post, record_to_multidict, LogicallyDeleted
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Account
from ticketing.accounts.forms import AccountForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Accounts(BaseView):

    @view_config(route_name='accounts.index', renderer='ticketing:templates/accounts/index.html')
    def index(self):
        current_page = int(self.request.params.get('page', 0))
        sort = self.request.GET.get('sort', 'Account.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        page_url = paginate.PageURL_WebOb(self.request)
        query = Account.filter(Account.organization_id==int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        accounts = paginate.Page(query.order_by(Account.id), page=current_page, items_per_page=10, url=page_url)

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

        form = AccountForm()
        form.process(record_to_multidict(account))
        return {
            'form':form,
            'account':account
        }

    @view_config(route_name='accounts.new', request_method='POST', renderer='ticketing:templates/accounts/_form.html')
    def new_post(self):
        f = AccountForm(self.request.POST)
        if f.validate():
            account = merge_session_with_post(Account(), f.data)
            account.organization_id = self.context.user.organization_id
            account.save()

            self.request.session.flash(u'アカウントを保存しました')
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

        f = AccountForm(self.request.POST)
        if f.validate():
            account = merge_session_with_post(account, f.data)
            account.organization_id = self.context.user.organization_id
            account.save()

            self.request.session.flash(u'アカウントを保存しました')
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

        account.delete()

        self.request.session.flash(u'アカウントを削除しました')
        return HTTPFound(location=route_path('accounts.index', self.request))
