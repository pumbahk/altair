from zope.interface import Interface, Attribute, implements
import re

from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid
from ticketing.operators.models import *

import sqlahelper
session = sqlahelper.get_session()

r = re.compile(r'^(/_deform)|(/static)|(/_debug_toolbar)|(/favicon.ico)')

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone        , 'everybody'),
        (Allow, Authenticated   , 'authenticated'),
        (Allow, 'login'         , 'everybody'),
        ]
    user = None
    def __init__(self, request):
        if not r.match(request.path):
            roles = OperatorRole.all()
            for role in roles:
                for permission in role.permissions:
                    print role.name
                    print role.permissions
                    self.__acl__.append((Allow, role.name, permission.category_name))
                    print role.name

            user_id = authenticated_userid(request)
            self.user = Operator.get_by_login_id(user_id) if user_id is not None else None
            print "-------"
            for acl in self.__acl__:
                print acl

def groupfinder(userid, request):
    user = session.query(Operator).filter(Operator.login_id == userid).first()
    if user is None:
        return []
    print [role.name for role in user.roles]
    return [role.name for role in user.roles]

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
