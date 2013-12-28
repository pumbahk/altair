# -*- coding:utf-8 -*-
from zope.interface import implementer
from altair.app.ticketing.login.internal.interfaces import IInternalAuthAPIResource
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, authenticated_userid
from altair.app.ticketing.operators.models import Operator, OperatorAuth
import logging
logger = logging.getLogger(__name__)

from .models import CheckinIdentity
from altair.app.ticketing.models import DBSession
from pyramid.security import remember
from datetime import datetime

@implementer(IInternalAuthAPIResource)
class CheckinStationResource(object):
    def __init__(self, request):
        self.request = request

    __acl__ = [
        (Allow, 'group:sales_counter', 'sales_counter'), 
        (Allow, Everyone, 'everybody'),
    ]

    @property
    def device_id(self):
        """ログイン時に渡される情報"""
        return self.request.json_body.get("device_id",
                                          self.request.client_addr)

    def on_after_login(self, operator):
        identity = CheckinIdentity(operator=operator, device_id=self.device_id)
        identity.login()
        DBSession.add(identity)
        DBSession.flush() #identityのidが欲しい

        ## operator.idだけでなくidentity.idも保持したいのでrememberし直し
        headers = remember(self.request, "@".join(map(str, [identity.id, operator.id])))
        self.request.response.headers = headers
        return {"endpoint": 
                {"login.status": self.request.route_url("login.status")}}

    def on_after_logout(self, operator):
        self.identity.logout()
        return {"message", "logout at {now}".format(now=datetime.now())}

    def login_validate(self, form):
        return form.validate()

    @reify
    def identity(self):
        identity_id, operator_id = authenticated_userid(self.request).split("@")
        return CheckinIdentity.query.filter_by(id=identity_id).one()

    @reify
    def operator(self):
        identity_id, operator_id = authenticated_userid(self.request).split("@")
        return Operator.query.filter(Operator.id==operator_id).one()

    @reify
    def organization(self):
        return self.operator.organization
