from zope.interface import Interface, Attribute, implements
import re

from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid

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
        pass

def groupfinder(userid, request):
    pass

class ActingAsBreadcrumb(Interface):
    navigation_parent = Attribute('')
    navigation_name = Attribute('')

class Titled(Interface):
    title = Attribute('')
