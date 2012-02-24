# coding: utf-8
from altaircms.models import DBSession
from altaircms.auth.models import Permission

def groupfinder(userid, request):
    objects = DBSession.query(Permission).filter_by(operator_id=userid)
    perms = []

    for obj in objects:
        perms.append(obj.permission)

    return perms

class SecurityAllOK(list):
    def __init__(self):
        from altaircms.auth.models import PERMISSION_VIEW, PERMISSION_EDIT
        self.perms_keys = PERMISSION_VIEW, PERMISSION_EDIT
        self.perms = None

    def __call__(self, user_id, request):
        if self.perms is None:
            self.perms = self._create_perms()
        return self.perms
        
    def _create_perms(self):
        return [Permission(operator_id=None, permission=p) \
                    for p in self.perms_keys]

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
