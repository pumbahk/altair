# -*- coding:utf-8 -*-
import logging
import itertools
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_request
from zope.interface import implementer
from . import api
from ..core import api as core_api
from .resources import TicketingCartResourceBase
from pyramid.httpexceptions import HTTPNotFound

logger = logging.getLogger(__name__)

class InvalidMemberGroupException(Exception):
    def __init__(self, event_id):
        Exception.__init__(self)
        self.event_id = event_id

@implementer(IAuthorizationPolicy)
class MembershipAuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        """
        principalsには、ユーザーの会員種別がすでに入っている想定
        """
        assert isinstance(context, TicketingCartResourceBase)

        request = context.request

        if 'buy' not in permission and not principals:
            return False

        if permission == "view":
            # 楽天認証
            return "auth_type:rakuten" in principals

        if permission == "buy":
            logger.debug('authorize for buy %s' % (principals,))
            if not context.login_required:
                if context.event is not None:
                    logger.debug('context.event %s do not require login' % context.event.title)
                else:
                    logger.debug('context.event is None')
                return True            

            principals = [p for p in principals if p != 'system.Everyone']
            return principals

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

