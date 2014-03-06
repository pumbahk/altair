# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implements
from zope.interface.verify import verifyObject
from pyramid.interfaces import IView, IRoutesMapper, IRouteRequest, IViewClassifier, IMultiView
from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid
from pyramid.decorator import reify

from altair.app.ticketing.operators.models import OperatorAuth, OperatorRole, Operator
from altair.app.ticketing.authentication.api import get_authentication_challenge_view

import sqlahelper
session = sqlahelper.get_session()


class ExemptionResource(object):
    __acl__ = [
        (Allow, Everyone        , 'everybody'),
        ]

    def __init__(self, *args, **kwargs):
        pass

class TicketingAdminResource(object):
    _base_acl = [
        (Allow, Everyone        , 'everybody'),
        (Allow, Authenticated   , 'authenticated'),
        (Allow, 'login'         , 'everybody'),
        (Allow, 'api'           , 'api'),
        ]

    # the same ACL is applied to every resource under.
    @reify
    def __acl__(self):
        acl = self._base_acl[:]
        # build ACL
        roles = OperatorRole.all()
        for role in roles:
            for permission in role.permissions:
                acl.append((Allow, role.name, permission.category_name))
        return acl

    def user_id(self):
        return self.user_id

    def user(self):
        return self.user

    @reify
    def organization(self):
        return self.user and self.user.organization

    def __init__(self, request):
        self.request = request
        self.user_id = authenticated_userid(self.request)
        self.user = Operator.get_by_login_id(self.user_id) if self.user_id is not None else None

def groupfinder(userid, request):
    user = session.query(Operator).join(OperatorAuth).filter(OperatorAuth.login_id == userid).first()
    if user is None:
        return []
    return [role.name for role in user.roles]
