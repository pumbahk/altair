# encoding: utf-8
from zope.interface import implementer, Interface
from pyramid.interfaces import IRoutesMapper, PHASE1_CONFIG
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from repoze.who.interfaces import IAuthenticator, IChallenger
from altair.auth.api import get_current_request, who_api
from altair.auth.rememberer.pyramid_session import PyramidSessionBasedRemembererPlugin
import functools

import logging

logger = logging.getLogger(__name__)

IDENTIFIER_NAME = 'nogizaka46'
CREDENTIAL_KEY = 'nogizaka46.key'

class INogizakaAuthInterceptor(Interface):
    def add_route(route_name):
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
        if opaque == self.preset_auth_key:
            logger.debug('opaque=%s' % opaque)
            return {
                'username': self.username,
                'membership': self.membership_name,
                }
        else:
            return None

@implementer(IAuthenticator, IChallenger)
class NogizakaAuthPlugin(object):
    def __init__(self, credential_key, backend):
        logger.debug('OK')
        self.credential_key = credential_key
        self.backend = backend

    def authenticate(self, environ, identity):
        logger.debug('%s: authenticate', self.__class__.__name__)
        request = get_current_request(environ)
        opaque = identity.get(self.credential_key)
        data = self.backend(request, opaque)
        if data is None:
            logger.debug('%s: authentication failed' , self.__class__.__name__)
            return None
        identity.update(data)
        identity['is_guest'] = False
        return identity['username']

    def challenge(self, environ, status, app_headers, forget_headers):
        return HTTPNotFound()


def nogizaka_entrypoint_predicate(context, request):
    api, _ = who_api(request, IDENTIFIER_NAME)
    keyword = request.POST.get('keyword')
    if keyword is not None:
        if not api.authenticate():
            # POSTでかつnogizaka46認証されていないときのみ、新規の認証を試みる
            identity, headers = api.login(
                { CREDENTIAL_KEY: keyword }
                )
            if identity:
                request.response.headers.update(headers)
        return True
    else:
        return False

def nogizaka_entrypoint_view(config, request):
    return HTTPFound(request.current_route_path())

def add_nogizaka_entrypoint(config, route_name):
    config.add_view(nogizaka_entrypoint_view, request_method='POST', request_param='keyword', route_name=route_name, custom_predicates=(nogizaka_entrypoint_predicate,))

def includeme(config):
    from altair.auth.facade import AugmentedWhoAPIFactory
    backend = CompatibilityBackendFactory(config)
    nogizaka_auth = NogizakaAuthPlugin(CREDENTIAL_KEY, backend)
    config.add_who_api_factory(
        IDENTIFIER_NAME,
        AugmentedWhoAPIFactory(
            authenticators=[(IDENTIFIER_NAME, nogizaka_auth)],
            challengers=[(IDENTIFIER_NAME, nogizaka_auth)],
            )
        )
    config.add_directive('add_nogizaka_entrypoint', add_nogizaka_entrypoint)

