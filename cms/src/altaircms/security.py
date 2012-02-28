# coding: utf-8
from pyramid.security import Allow, Authenticated, Everyone, Deny, DENY_ALL

from altaircms.models import DBSession

from altaircms.auth.models import Operator, Role, RolePermission

def rolefinder(userid, request):
    """
    ユーザIDを受け取って所属ロール一覧を返す

    :return: list 所属ロール名のリスト
    """
    roles = map(str, [role.name for role in DBSession.query(Role).filter(Operator.user_id==userid).filter(Role.id==Operator.role_id)])
    return roles


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None
    __acl__ = []

    def __init__(self, request):
        self.__acl__ = [
            (Allow, Authenticated, 'authenticated'),
            DENY_ALL,
        ]
        for role, permission in DBSession.query(Role, RolePermission).filter(Role.id==RolePermission.role_id):
            self.__acl__.append((Allow,) + (str(role.name), str(permission.permission)))


class SecurityAllOK(list):
    def __init__(self):
        from altaircms.auth.models import PERMISSIONS
        self.perms = PERMISSIONS

    def __call__(self, user_id, request):
        return self.perms


from zope.interface import implements
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.location import lineage
from pyramid.security import ACLAllowed
class DummyAuthorizationPolicy(object):
    implements(IAuthorizationPolicy)
    def permits(self, context, principals, permission):
        acl = '<No ACL found on any object in resource lineage>'
        
        for location in lineage(context):
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                return ACLAllowed(ace, acl, permission,
                                  principals, location)
                

    def principals_allowed_by_permission(self, context, permission):
        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            try:
                acl = location.__acl__
            except AttributeError:
                continue

            allowed_here = set()
            denied_here = set()
            
            for ace_action, ace_principal, ace_permissions in acl:
                if not hasattr(ace_permissions, '__iter__'):
                    ace_permissions = [ace_permissions]
                if not ace_principal in denied_here:
                    allowed_here.add(ace_principal)
            allowed.update(allowed_here)
        return allowed
