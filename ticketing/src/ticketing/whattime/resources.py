from pyramid.security import Allow, Everyone
from zope.interface import implementer
from ticketing.login.internal.interfaces import IInternalAuthResource

@implementer(IInternalAuthResource)
class CartAdminResource(object):
    def __init__(self, request):
        self.request = request
        
    __acl__ = [
        (Allow, 'group:cart_admin', 'cart_admin'), 
        (Allow, Everyone, 'everybody'),]

    def get_after_login_url(self, *args, **kwargs):
        return self.request.route_path("whattime.nowsetting.form", *args, **kwargs)
