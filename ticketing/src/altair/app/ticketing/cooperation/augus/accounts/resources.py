# -*- coding: utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound
from pyramid.decorator import reify

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import AugusAccount


class AugusAccountResourceBase(TicketingAdminResource):
    def __init__(self, request):
        super(AugusAccountResourceBase, self).__init__(request)
        self._load_request(request)

    def _load_request(self, request):
        raise NotImplementedError('Not implemented error.')


class AugusAccountListResource(AugusAccountResourceBase):
    def _load_request(self, request):
        pass

    @reify
    def augus_accounts(self):
        return [account.augus_account
                for account in self.organization.accounts
                if account.augus_account
                ]


class AugusAccountResource(AugusAccountResourceBase):
    def __init__(self, request):
        super(type(self), self).__init__(request)
        self._load_request(request)

    def _load_request(self, request):
        self.augus_account_id = request.matchdict.get('augus_account_id', None)
        if self.augus_account_id:
            self.augus_account_id = int(self.augus_account_id)

    @reify
    def augus_account(self):
        augus_account = None
        try:
            if self.augus_account_id:
                augus_account = AugusAccount\
                    .query\
                    .filter(AugusAccount.id==self.augus_account_id)\
                    .one()
        except NoResultFound:
            pass
        return augus_account
