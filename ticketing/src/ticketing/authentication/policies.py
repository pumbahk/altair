from pyramid.security import Everyone, Authenticated
from pyramid.interfaces import IDebugLogger, IAuthenticationPolicy
from zope.interface import implementer
from .apikey.api import get_apikeyentry, set_apikeyentry

__all__ = [
    'CombinedAuthenticationPolicy',
    'APIAuthenticationPolicy',
    ]

@implementer(IAuthenticationPolicy)
class CombinedAuthenticationPolicy(object):
    """Authentication policy that delegates operations to other authentication policies until it succeeds"""

    debug = False

    def _log(self, msg):
        logger = request.registry.queryUtility(IDebugLogger)
        if logger is not None:
            logger.debug(msg)

    def __init__(self, policies, debug=False):
        self.policies = policies
        self.debug = debug

    def authenticated_userid(self, request):
        for policy in self.policies:
            userid = policy.authenticated_userid(request)
            if userid is not None:
                self.debug and self._log("authenticated_userid: policy=%s", policy)
                return userid

    def unauthenticated_userid(self, request):
        for policy in self.policies:
            userid = policy.unauthenticated_userid(request)
            if userid is not None:
                self.debug and self._log("unauthenticated_userid: policy=%s", policy)
                return userid

    def effective_principals(self, request):
        resulting_principals = set()
        for policy in self.policies:
            principals = policy.effective_principals(request)
            resulting_principals.update(principals)
        return list(resulting_principals)

    def remember(self, request, principal, **kw):
        resulting_headers = []
        for policy in self.policies:
            resulting_headers += policy.remember(request, principal, **kw)
        return resulting_headers

    def forget(self, request):
        resulting_headers = []
        for policy in self.policies:
            resulting_headers += policy.forget(request)
        return resulting_headers

@implementer(IAuthenticationPolicy)
class APIAuthenticationPolicy(object):
    def __init__(self, resolver_factory, header_name, userid_prefix, principals=[]):
        self.header_name = header_name
        self.userid_prefix = userid_prefix
        self.principals = principals
        self.resolver = resolver_factory(userid_prefix)

    def authenticated_userid(self, request):
        userid = self.unauthenticated_userid(request)
        apikeyentry = self.resolver(userid, request)
        if apikeyentry is None:
            return None
        else:
            set_apikeyentry(request, apikeyentry)
            return userid

    def unauthenticated_userid(self, request):
        apikey = request.headers.get(self.header_name)
        if apikey is None:
            return None
        return self.userid_prefix + apikey

    def effective_principals(self, request):
        apikeyentry = get_apikeyentry(request)
        retval = [Everyone]
        if apikeyentry is not None:
            retval.extend([Authenticated, apikeyentry.userid])
            retval.extend(self.principals)
            retval.extend(apikeyentry.principals)
        return retval

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []
