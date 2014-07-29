# -*- coding: utf-8 -*-
from pyramid.view import (
    view_config,
    view_defaults,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPBadRequest,
    )
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.core.models import AugusAccount
from .forms import AugusAccountForm


@view_defaults(route_name='augus.accounts', decorator=with_bootstrap, permission='administrator')
class AugusAccountListView(BaseView):
    @view_config(route_name='augus.accounts.index', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/index.html')
    def get(self):
        return {
            'augus_accounts': self.context.augus_accounts,
            }

@view_defaults(route_name='augus.accounts', decorator=with_bootstrap, permission='administrator')
class AugusAccountCreateView(BaseView):
    @view_config(route_name='augus.accounts.create', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/edit.html')
    def get(self):
        form = AugusAccountForm(organization_id=self.context.organization.id)
        return {
            'form': form,
            }

    @view_config(route_name='augus.accounts.create', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/edit.html')
    def post(self):
        form = AugusAccountForm(self.request.params, organization_id=self.context.organization.id)
        if form.validate():
            augus_account = AugusAccount()
            augus_account = merge_session_with_post(augus_account, form.data)
            augus_account.organization_id = self.context.organization.id
            augus_account.save()
            url = self.request.route_path('augus.accounts.show', augus_account_id=augus_account.id)
            return HTTPFound(location=url)
        else:
            return {
                'form': form,
                }

@view_defaults(route_name='augus.accounts', decorator=with_bootstrap, permission='administrator')
class AugusAccountEditView(BaseView):
    @view_config(route_name='augus.accounts.edit', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/edit.html')
    def get(self):
        if not self.context.augus_account:
            raise HTTPNotFound(u'AugusAccount ot found: id={}'.format(self.context.augus_account_id))

        form = AugusAccountForm(obj=self.context.augus_account, organization_id=self.context.organization.id)
        return {
            'form': form,
            }

    @view_config(route_name='augus.accounts.edit', request_method='POST',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/edit.html')
    def post(self):
        form = AugusAccountForm(self.request.params, organization_id=self.context.organization.id)
        if form.validate():
            augus_account = self.context.augus_account
            now_password = augus_account.password

            augus_account = merge_session_with_post(augus_account, form.data)
            if not augus_account.password.strip():
                augus_account.password = now_password
            augus_account.organization_id = self.context.organization.id
            augus_account.save()
            url = self.request.route_path('augus.accounts.show', augus_account_id=augus_account.id)
            return HTTPFound(location=url)
        else:
            return {
                'form': form,
                }


@view_defaults(route_name='augus.accounts', decorator=with_bootstrap, permission='administrator')
class AugusAccountShowView(BaseView):
    @view_config(route_name='augus.accounts.show', request_method='GET',
                 renderer='altair.app.ticketing:templates/cooperation/augus/accounts/show.html')
    def get(self):
        if not self.context.augus_account:
            raise HTTPNotFound(u'AugusAccount ot found: id={}'.format(self.context.augus_account_id))

        return {
            'augus_account': self.context.augus_account,
            }


@view_defaults(route_name='augus.accounts', decorator=with_bootstrap, permission='administrator')
class AugusAccountDeleteView(BaseView):
    @view_config(route_name='augus.accounts.delete', request_method='POST')
    def post(self):
        if not self.context.augus_account:
            raise HTTPNotFound(u'AugusAccount ot found: id={}'.format(self.context.augus_account_id))
        augus_account = self.context.augus_account
        session = DBSession
        session.delete(augus_account)
        url = self.request.route_path('augus.accounts.index')
        return HTTPFound(url)
