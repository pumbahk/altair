# -*- encoding:utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from zope.interface import implementer
import urllib
import logging
logger = logging.getLogger(__file__)

from pyramid.security import forget

from .interfaces import ILogoutAction
from .interfaces import IActionResult
from .interfaces import IOAuthComponent
from .interfaces import IAllowableQueryFactory
from .subscribers import AfterLogin
from altaircms.auth.helpers import get_authenticated_user
from pyramid.security import unauthenticated_userid

def require_login(info, request):
    """custom predicates"""
    ## this process has DB access.
    # return bool(getattr(request, "user", None))
    return bool(unauthenticated_userid(request))

def get_logout_action(request):
    return request.registry.getUtility(ILogoutAction)

def get_oauth_component(request):
    return request.registry.getUtility(IOAuthComponent)

def notify_after_oauth_login(request, data):
    return request.registry.notify(AfterLogin(request, data))

def forget_self(request):
    headers = forget(request)

    ## キャッシュしていたoperatorのデータをリフレッシュ.
    request.set_property(get_authenticated_user, "user", reify=True)
    return headers


@implementer(ILogoutAction)
class LogoutSelfOnly(object):
    def __init__(self, external_url):
        self.external_url = external_url

    def logout(self, request):
        headers = forget_self(request)
        location = make_url_noaction(request)
        return ActionResult(location, headers)


def make_url_noaction(request):
    return request.resource_url(request.context)


@implementer(ILogoutAction)
class LogoutWithBackend(object):
    def __init__(self, external_url):
        self.external_url = external_url

    def logout(self, request):
        headers = forget_self(request)
        location = make_external_logout_url(request, self.external_url)
        return ActionResult(location, headers)


def make_external_logout_url(request, url):
    return_to = request.resource_url(request.context)
    params = dict(return_to=return_to)
    return u"%s?%s" % (url, urllib.urlencode(params))
    
@implementer(IActionResult)
class ActionResult(dict):
    def __init__(self, return_to, headers=None):
        self.return_to = return_to
        self.headers = headers


@implementer(IOAuthComponent)
class OAuthComponent(object):
    def __init__(self, client_id, secret_key, authorize_url, access_token_url):
        self.client_id = client_id
        self.secret_key = secret_key
        self.authorize_url = authorize_url
        self.access_token_url = access_token_url
    
    def create_oauth_entry_url(self):
        url = '%s?client_id=%s&response_type=code' %(self.authorize_url, self.client_id)
        return url

    def create_oauth_token_url(self, code, grant_type='authorization_code'):
        args = dict(
            client_id=self.client_id,
            client_secret=self.secret_key,
            code=code,
            grant_type=grant_type)
        
        url = self.access_token_url +"?" + urllib.urlencode(args)
        return url

###login後の絞り込み
@implementer(IAllowableQueryFactory)
class AllowableQueryFactory(object):
    def __init__(self, model):
        assert hasattr(model, "organization_id")
        self.model = model

    def __call__(self, request, query=None):
        return query

def get_allowable_query(request):
    def query(model, qs=None):
        qs = qs or model.query
        if request.organization:
            return qs.with_transformation(request.organization.inthere("organization_id"))
        logger.debug("this-is-external-request. e.g. access with pageaccess key. request.organization is not found")
    return query

def get_or_404(qs, criteria):
    r = qs.filter(criteria).first()
    if r is None:
        raise HTTPNotFound("----")
    return r

# def raise_error_if_notallowable(request, obj):
#     if request.organization.id != obj.organization_id:
#         raise HTTPForbidden(u"閲覧権限を持っていません")
