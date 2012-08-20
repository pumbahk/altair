# -*- coding:utf-8 -*-

from pyramid.interfaces import IAuthorizationPolicy
from zope.interface import implementer

@implementer(IAuthorizationPolicy)
class MembershipAuthorizationPolicy(object):
    def __init__(self):
        pass


    def permit(self, context, principals, permission):
        """
        principalsには、ユーザーの会員種別がすでに入っている想定
        """

        membership = context.membership    
        membergroup = context.membergroup
        if membership is None or membergroup is None:
            # 楽天認証
            return "rakuten_user" in principals

        permit_membership = "membership:%s" % membership in principals
        permit_membergroup = "membergroup:%s" % membergroup in principals
        return permit_membership and permit_membergroup

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

