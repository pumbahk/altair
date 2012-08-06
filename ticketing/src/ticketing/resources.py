from zope.interface import Interface, Attribute, implements
from zope.interface.verify import verifyObject

from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid
from .operators.models import OperatorAuth, OperatorRole, Operator

import sqlahelper
session = sqlahelper.get_session()

def newRootFactory(exemption_matcher):
    acl = [
        (Allow, Everyone        , 'everybody'),
        (Allow, Authenticated   , 'authenticated'),
        (Allow, 'login'         , 'everybody'),
        (Allow, 'api'           , 'api'),
        ]

    # build ACL
    roles = OperatorRole.all()
    for role in roles:
        for permission in role.permissions:
            acl.append((Allow, role.name, permission.category_name))

    class Root(object):
        # the same ACL is applied to every resource under.
        __acl__ = acl

        def __init__(self, request):
            if exemption_matcher(request):
                return None
            user_id = authenticated_userid(request)
            # assign the operator object to the context
            self.user = Operator.get_by_login_id(user_id) if user_id is not None else None
            self.request = request

    return Root

def groupfinder(userid, request):
    user = session.query(Operator).join(OperatorAuth).filter(OperatorAuth.login_id == userid).first()
    if user is None:
        return []
    return [role.name for role in user.roles]

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
