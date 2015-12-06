from zope.interface import implementer
from altair.rakuten_auth.interfaces import IRakutenOpenIDURLBuilder
from urlparse import urljoin

PREFIX = 'altair.rakuten_auth.claimed_id:'

def get_openid_claimed_id(request):
    for principal in request.effective_principals:
        if principal.startswith(PREFIX):
            return principal[len(PREFIX):]
    return None

def add_claimed_id_to_principals(identities, request):
    if 'rakuten' in identities:
        return ['%s%s' % (PREFIX, identities['rakuten']['claimed_id'])]
    return []

def get_rakuten_auth_setting(request, k):
    settings = request.organization.settings
    if settings is not None:
        rakuten_auth_settings = settings.get(u'rakuten_auth')
        if rakuten_auth_settings is not None:
            return rakuten_auth_settings.get(k)
    return None

def consumer_key_builder(request):
    return get_rakuten_auth_setting(request, u'oauth_consumer_key')

def consumer_secret_builder(request):
    return get_rakuten_auth_setting(request, u'oauth_consumer_secret')

@implementer(IRakutenOpenIDURLBuilder)
class OrganizationSettingsBasedRakutenAuthURLBuilder(object):
    def __init__(self, **kwargs):
        pass

    def extra_verify_url_exists(self, request):
        return get_rakuten_auth_setting(request, u'proxy_url_pattern') is not None

    def build_base_url(self, request):
        proxy_url_pattern = get_rakuten_auth_setting(request, u'proxy_url_pattern')
        subdomain = request.host.split('.', 1)[0]
        return proxy_url_pattern.format(
            subdomain=subdomain
            )

    def build_return_to_url(self, request):
        if self.extra_verify_url_exists(request):
            return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.verify').lstrip('/'))
        else:
            return request.route_url('rakuten_auth.verify')

    def build_error_to_url(self, request):
        if self.extra_verify_url_exists(request):
            return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.error').lstrip('/'))
        else:
            return request.route_url('rakuten_auth.error')

    def build_verify_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_extra_verify_url(self, request):
        if self.extra_verify_url_exists(request):
            return request.route_url('rakuten_auth.verify2')
        else:
            return None
