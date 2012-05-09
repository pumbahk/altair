 # -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.models import DBSession, merge_session_with_post
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
        query = DBSession.query(Account).order_by(sort + ' ' + direction)
        query = query.filter(Account.organization_id == int(self.context.user.organization_id))

        accounts = paginate.Page(query.order_by(Account.id), page=current_page, items_per_page=10, url=page_url)

        f = AccountForm()
        return {
            'form':f,
            'accounts':accounts,
        }

    @view_config(route_name='accounts.show', renderer='ticketing:templates/accounts/show.html')
    def show(self):
        account_id = int(self.request.matchdict.get('account_id', 0))
        account = Account.get(account_id)
        if account is None:
            return HTTPNotFound('account id %d is not found' % account_id)

        f = AccountForm()
        return {
            'form':f,
            'account':account,
        }

    @view_config(route_name='accounts.new', request_method='POST')
    def new_post(self):
        f = AccountForm(self.request.POST)

        if f.validate():
            account = merge_session_with_post(Account(), f.data)
            account.organization_id = self.context.user.organization_id
            account.save()

            self.request.session.flash(u'アカウントを登録しました')
        return HTTPFound(location=route_path('accounts.index', self.request))
