# -*- coding:utf-8 -*-
import logging
import itertools
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_request
from zope.interface import implementer
from . import api

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
        request = context.request

        if 'buy' not in permission and not principals:
            return False

        if permission == "view":
            # 楽天認証
            return "rakuten_auth" in principals

        if permission == "buy":
            logger.debug('authorize for buy %s' % (principals,))
            sales_segments = context.sales_segments

            event = api.get_event(request)
            if not event:
                logger.debug('no event')
                return True

            if not api.is_login_required(request, event):
                logger.debug('event %s do not require login' % event.title)
                return True            

            principals = [p for p in principals if p != 'system.Everyone']
            return principals

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

