# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute, implements
from zope.interface.verify import verifyObject
from pyramid.interfaces import IView, IRoutesMapper, IRouteRequest, IViewClassifier, IMultiView
from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid
from pyramid.decorator import reify
from sqlalchemy.orm import joinedload

from altair.app.ticketing.core.models import DBSession
from altair.app.ticketing.operators.models import OperatorAuth, OperatorRole, Operator
from altair.app.ticketing.authentication.api import get_authentication_challenge_view

import sqlahelper


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
        roles = OperatorRole.query.options(joinedload(OperatorRole.permissions)).all()
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
    if hasattr(request, 'context') and hasattr(request.context, 'user') \
       and request.context.user is not None and request.context.user.auth.login_id == userid:
        user = request.context.user
    else:
        user = Operator.get_by_login_id(userid)
        if user is None:
            return []
    return [role.name for role in user.roles]
