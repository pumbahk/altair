# coding: utf-8
from pyramid.security import Allow, Authenticated, Everyone, Deny, DENY_ALL

from altaircms.models import DBSession

from altaircms.auth.models import Operator, RolePermission

def groupfinder(userid, request):
    """
    ユーザIDを受け取ってpermission一覧を返す
    """
    operator = DBSession.query(Operator).filter_by(user_id=userid).one()
    return [q.permission for q in DBSession.query(RolePermission).filter_by(role_id=operator.role_id)]


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None
    __acl__ = [
        # auth state, username or groupname, permission
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'event_', 'event_viewer'),
        (Allow, 'ticket', 'ticket_viewer'),
        (Allow, 'page', 'page_viewer'),
        (Allow, 'page_editor', 'page_viewer'),
        (Allow, 'page_editor', 'page_editor'),
        (Allow, 'topic', 'topic_viewer'),
        (Allow, 'topic_editor', 'topic_viewer'),
        (Allow, 'topic_editor', 'topic_editor'),
        (Allow, 'magazine', 'magazine_viewer'),
        (Allow, 'magazine_editor', 'magazine_viewer'),
        (Allow, 'magazine_editor', 'magazine_editor'),

        # administrator have all permissions
        (Allow, 'admin', 'event_viewer'),
        (Allow, 'admin', 'ticket_viewer'),
        (Allow, 'admin', 'page_editor'),
        (Allow, 'admin', 'topic_editor'),
        (Allow, 'admin', 'magazine_editor'),
        (Allow, 'admin', 'administrator'),
        DENY_ALL,
        ]

    def __init__(self, request):
        pass
ALTAIRCMS_ACL = [
    (Allow, Authenticated, 'authenticated'),
    DENY_ALL,
]

RootFactory.__acl__ = ALTAIRCMS_ACL


class SecurityAllOK(list):
    def __init__(self):
        from altaircms.auth.models import PERMISSIONS
        self.perms_keys = PERMISSIONS
        self.perms = None

    def __call__(self, user_id, request):
        if self.perms is None:
            self.perms = self._create_perms()
        return self.perms
        
    def _create_perms(self):
        #return [Permission(operator_id=None, permission=p) \
        #             for p in self.perms_keys]
        return None


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
