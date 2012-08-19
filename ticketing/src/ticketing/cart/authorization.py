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
        if membership is None:
            # 楽天認証
            return "rakuten_user" in principals

        return "membership:%s" % membership in principals

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

