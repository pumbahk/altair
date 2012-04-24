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
        (Allow, 'administrator' , 'administrator'),
        ]
    user = None
    def __init__(self, request):
        if not r.match(request.path):
            user_id = authenticated_userid(request)
            self.user = Operator.get_by_login_id(user_id) if user_id is not None else None

def groupfinder(userid, request):
    user = session.query(Operator).filter(Operator.login_id == userid).first()
    if user is None:
        return []
    permissions = []
    for g in user.roles:
        for category_name in [p.category_name for p in g.permissions]:
            permissions.append(category_name)
    print permissions
    return permissions

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
