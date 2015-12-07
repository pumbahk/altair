# encoding: utf-8
import logging
import functools
from zope.interface import implementer, Interface
from pyramid.interfaces import IRoutesMapper, PHASE1_CONFIG
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altair.auth.interfaces import IAuthenticator, ILoginHandler
from altair.auth.api import get_who_api
from altair.app.ticketing.cart import ICartResource
from altair.app.ticketing.lots import ILotResource

logger = logging.getLogger(__name__)

IDENTIFIER_NAME = 'nogizaka46'
CREDENTIAL_KEY = 'nogizaka46.key'

class INogizakaAuthEntrypoint(Interface):
    def interceptor(self, context, request):
        pass

class CompatibilityBackendFactory(object):
    def __init__(self, config):
        settings = config.registry.settings
        preset_auth_key = settings.get('altair.nogizaka46_auth.key')
        if preset_auth_key is None:
            preset_auth_key = settings['altair.lots.nogizaka_auth_key']

        self.preset_auth_key = preset_auth_key
        self.username = settings.get('altair.nogizaka46_auth.username', '::nogizaka46::')
        self.membership_name = settings.get('altair.nogizaka46_auth.membership', 'nogizaka46')

    def __call__(self, request, opaque):
        logger.debug('opaque=%s, preset_auth_key=%s' % (opaque, self.preset_auth_key))
        auth_key = self.preset_auth_key
        context = getattr(request, 'context', None)
        if context is not None:
            if ICartResource.providedBy(context) or ILotResource.providedBy(context):
                cart_setting = context.cart_setting
                if cart_setting is not None:
                    auth_key_from_cart_setting = cart_setting.nogizaka46_auth_key
                    if auth_key_from_cart_setting is not None:
                        auth_key = auth_key_from_cart_setting
        if opaque == auth_key:
            return {
                'username': self.username,
                'membership': self.membership_name,
                'is_guest': True,
                }
        else:
            return None

@implementer(IAuthenticator, ILoginHandler)
class NogizakaAuthPlugin(object):
    name = IDENTIFIER_NAME

    def __init__(self, credential_key, backend):
        logger.debug('OK')
        self.credential_key = credential_key
        self.backend = backend

    def get_auth_factors(self, request, auth_context, credentials):
        return credentials 

    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('%s: authenticate', self.__class__.__name__)
        auth_factor = {}
        for _auth_factor in auth_factors.values():
            auth_factor.update(_auth_factor)
        opaque = auth_factor.get(self.credential_key)
        identity = self.backend(request, opaque)
        if identity is None:
            logger.debug('%s: authentication failed' , self.__class__.__name__)
            return None, None
        remembered_auth_factors = { self.credential_key: opaque } 
        return identity, { session_keeper.name: remembered_auth_factors for session_keeper in auth_context.session_keepers }

    def interceptor(self, context, request):
        api = get_who_api(request)
        keyword = request.POST.get('keyword')
        if keyword is not None:
            identities, auth_factors, metadata = api.authenticate()
            if identities is None or identities.get(self.name) is None:
                # POSTでかつnogizaka46認証されていないときのみ、新規の認証を試みる
                identities, headers, metadata, response = api.login(
                    { self.credential_key: keyword }
                    )
                if identities:
                    request.response.headers.update(headers)
            return True
        else:
            return False

def nogizaka_entrypoint_view(config, request):
    return HTTPFound(request.current_route_path())

def nogizaka_entrypoint_predicate(context, request):
    return request.registry.queryUtility(INogizakaAuthEntrypoint).interceptor(context, request)

def add_nogizaka_entrypoint(config, route_name):
    config.add_view(nogizaka_entrypoint_view, request_method='POST', request_param='keyword', route_name=route_name, custom_predicates=(nogizaka_entrypoint_predicate,))

def includeme(config):
    backend = CompatibilityBackendFactory(config)
    nogizaka_auth = NogizakaAuthPlugin(CREDENTIAL_KEY, backend)
    config.add_auth_plugin(nogizaka_auth)
    config.registry.registerUtility(nogizaka_auth, INogizakaAuthEntrypoint)
    config.add_directive('add_nogizaka_entrypoint', add_nogizaka_entrypoint)

