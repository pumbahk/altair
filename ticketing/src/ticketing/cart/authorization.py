# -*- coding:utf-8 -*-
import logging
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_request
from zope.interface import implementer

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
        if permission and not principals:
            return False

        if permission == "view":
            # 楽天認証
            return "rakuten_auth" in principals

        if permission == "buy":
            logger.debug('authorize for buy')
            membership = context.membership    
            membergroup = context.membergroup
            if membership is None or membergroup is None:
                # 楽天認証
                return "rakuten_auth" in principals

            
            membership_principal = "membership:%s" % membership.name
            membergroup_principal = "membergroup:%s" % membergroup.name
            permit_membership = membership_principal in principals
            permit_membergroup = membergroup_principal in principals
            if not permit_membership:
                logger.debug("%s not in %s" % (membership_principal, principals))
                return False

            if not permit_membergroup:
                raise InvalidMemberGroupException(context.event_id)

            return permit_membership and permit_membergroup

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

