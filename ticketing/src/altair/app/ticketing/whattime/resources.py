from pyramid.decorator import reify
from pyramid.security import Allow, Everyone
from zope.interface import implementer
from altair.app.ticketing.login.internal.interfaces import IInternalAuthResource
from altair.app.ticketing.core.api import get_organization
from altair.preview.data import OperatorPermissionData
from altair.preview.api import get_preview_secret

@implementer(IInternalAuthResource)
class WhattimeAdminResource(object):
    def __init__(self, request):
        self.request = request
        
    __acl__ = [
        (Allow, 'group:cart_admin', 'cart_admin'), 
        (Allow, Everyone, 'everybody'),]

    @reify
    def organization(self):
        return get_organization(self.request)

    def get_after_login_url(self, *args, **kwargs):
        return self.request.route_path("whattime.nowsetting.form", *args, **kwargs)

    def login_validate(self, form):
        if not (form.validate() and unicode(form.operator.organization_id) == unicode(self.organization.id)):
            return False

        secret = get_preview_secret(self.request)(form.operator.id)
        OperatorPermissionData.create(form.operator, secret=secret).dump(self.request)
        return True
