# coding: utf-8
import logging
from pyramid.security import Allow, Authenticated
from sqlalchemy.orm.exc import NoResultFound

from altaircms.models import DBSession
from altaircms.auth.models import Operator, Role

from zope.interface import implements
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.location import lineage
from pyramid.security import ACLAllowed
import itertools


def rolefinder(userid, request):
    """
    ユーザIDを受け取ってロール一覧を返す

    :return: list ユーザのロールリスト
    """
    try:
        operator = Operator.query.filter_by(user_id=userid).one()
        return [operator.role.name]
    except NoResultFound, e:
        logging.exception(e)
        return []


# データモデルから取得したACLをまとめる
class RootFactory(object):
    __name__ = None

    def __init__(self, request):
        self.request = request

    @property
    def __acl__(self):
        return [(Allow, Authenticated, 'authenticated')] + list(itertools.chain.from_iterable(
            [[(Allow, str(role.name), perm) 
              for perm in role.permissions] 
             for role in Role.query]))


class SecurityAllOK(list):
    def __init__(self):
        from altaircms.auth.models import DEFAULT_ROLE
        self.roles = [DEFAULT_ROLE]
        
    def __call__(self, user_id, request):
        return self.roles


class DummyAuthorizationPolicy(object):
    implements(IAuthorizationPolicy)
    def permits(self, context, principals, permission):
        acl = '<No ACL found on any object in resource lineage>'
        
        for location in lineage(context):
            if not hasattr(location, "__acl__"):
                continue

            acl = location.__acl__

            for ace in acl:
                ace_action, ace_principal, ace_permissions = ace
                return ACLAllowed(ace, acl, permission,
                                  principals, location)
                

    def principals_allowed_by_permission(self, context, permission):
        allowed = set()

        for location in reversed(list(lineage(context))):
            # NB: we're walking *up* the object graph from the root
            if not hasattr(location, "__acl__"):
                continue

            acl = location.__acl__

            allowed_here = set()
            denied_here = set()
            for ace_action, ace_principal, ace_permissions in acl:
                if not hasattr(ace_permissions, '__iter__'):
                    ace_permissions = [ace_permissions]
                if not ace_principal in denied_here:
                    allowed_here.add(ace_principal)
            allowed.update(allowed_here)
        return allowed
