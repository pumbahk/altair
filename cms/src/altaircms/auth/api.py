# -*- encoding:utf-8 -*-


from zope.interface import implementer
import urllib

from pyramid.security import forget

from .interfaces import ILogoutAction
from .interfaces import IActionResult
from altaircms.auth.helpers import get_authenticated_user


def get_logout_action(request):
    return request.registry.getUtility(ILogoutAction)


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

