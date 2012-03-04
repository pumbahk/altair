from zope.interface import Interface, Attribute, implements
# import oauth.oauth as oauth
# from ticketing.models.oauth_data_store import AltairAuthDataStore

REALM = 'http://altair.example.net/'


from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid

from ticketing.models import DBSession, Operator

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone        , 'everybody'),
        (Allow, Authenticated   , 'authenticated'),
        (Allow, 'login'         , 'everybody'),
        (Allow, 'test'          , ('admin')),
        ]

    def __init__(self, request):
        user_id = authenticated_userid(request)
        self.user = Operator.get_by_login_id(user_id) if user_id is not None else None

def groupfinder(userid, request):
    user = DBSession.query(Operator).filter(Operator.login_id == userid).first()
    if user is None:
        return []
    return [g.name for g in user.roles]

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
