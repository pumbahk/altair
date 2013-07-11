# This package may contain traces of nuts
import os
import logging
import sys
from pyramid.interfaces import IRequest
from pyramid.path import AssetResolver
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Everyone, Authenticated
from pyramid.tweens import EXCVIEW, INGRESS
from pyramid.response import Response
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IAPIFactory, IAPI
from repoze.who.config import make_api_factory_with_config
from zope.interface import implementer
from .interfaces import IWHOAPIDecider

logger = logging.getLogger(__name__)

REQUEST_KEY = 'altair.auth.request'

def set_who_api_decider(config, callable):
    callable = config.maybe_dotted(callable)
    reg = config.registry

    def register():
        reg.adapters.register([IRequest], IWHOAPIDecider, "", callable)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='who api decider',
                                 title='altair.auth WHO API Decider',
                                 type_name=str(callable))
    intr['callable'] = callable

    config.action('altair.auth.set_who_api_decider', register,
                  introspectables=(intr,))

    

def add_who_api_factory(config, name, api_spec):
    assets = AssetResolver(config.package)
    reg = config.registry
    resolver = assets.resolve(api_spec)
    ini_file = resolver.abspath()

    def register():
        global_conf = {'here': os.path.dirname(ini_file)}
        who_api_factory = make_api_factory_with_config(global_conf,
                                                       ini_file)
        reg.registerUtility(who_api_factory, name=name)

    intr = config.introspectable(category_name='altair.auth',
                                 discriminator='who api factory',
                                 title='{name} {api_spec}'.format(name=name, api_spec=api_spec),
                                 type_name=str(IAPIFactory))
    intr['ini_file'] = ini_file
    config.action('altair.auth.add_who_api_factory.{0}'.format(name), register,
                  introspectables=(intr,))
    logger.debug('who api {0}'.format(ini_file))


def activate_who_api(request):
    api_name = decide(request)
    api = who_api(request, api_name)
    request.environ['repoze.who.plugins'] = api.name_registry # BBB?

# def activate(request):
#     activate_who_api(request)
#     request.environ[REQUEST_KEY] = request

def deactivate(request):
    try:
        del request.environ[REQUEST_KEY]
    except KeyError:
        logger.error('exception ignored', exc_info=sys.exc_info())

def activate_who_api_tween(handler, registry):
    def wrap(request):
        try:
            #activate(request)
            request.environ[REQUEST_KEY] = request
            return handler(request)
        finally:
            deactivate(request)
    return wrap

def decide(request):
    decider = request.registry.getAdapter(request, IWHOAPIDecider)
    return decider.decide()


def who_api_factory(request, name):
    reg = request.registry
    return reg.queryUtility(IAPIFactory, name=name)

def list_who_api_factory(request):
    reg = request.registry
    return list(reg.getUtilitiesFor(IAPIFactory))


def who_api(request, name=""):
    factory = who_api_factory(request, name=name)
    if factory is None:
        return None
    api = factory(request.environ)
    return api

class ChallengeView(object):
    def __init__(self, request):
        self.request = request

    def __call__(self):
        api_name = decide(self.request)
        logger.debug('api_name=%s' % api_name)
        api = who_api(self.request, api_name)
        wsgi_resp = api.challenge()
        if wsgi_resp is None:
            msg = u'authentication failed where no challenge mechanism is provided'
            logger.warning(msg)
            return Response(status=403, body=u'We are experiencing a system error that you cannot work around at the moment. Sorry for the inconvenience... (guru meditation: {0})'.format(msg), content_type='text/plain')
        else:
            return self.request.get_response(wsgi_resp)


@implementer(IAuthenticationPolicy)
class MultiWhoAuthenticationPolicy(object):
    def __init__(self, identifier_id, callback=None):

        self._identifier_id = identifier_id
        self._callback = callback


    def __repr__(self):
        return "{0} identifier_id={1}, callback={2}".format(str(type(self)), self._identifier_id, str(self._callback))

    def unauthenticated_userid(self, request):
        identity = self._get_identity(request)
        if identity is not None:
            return identity['repoze.who.userid']

    def authenticated_userid(self, request):
        """ See IAuthenticationPolicy.
        """

        identity = self._get_identity(request)

        if identity is not None:
            groups = self._callback(identity, request)
            if groups is not None:
                return identity['repoze.who.userid']

    def effective_principals(self, request):
        """ See IAuthenticationPolicy.
        """

        identity = self._get_identity(request)
        if identity is None:
            return [Everyone]

        groups = self._get_groups(identity, request)
        if len(groups) > 1:
            if 'auth_type' in identity:
                groups.insert(0, "auth_type:%s" % identity['auth_type'])
            groups.insert(0, identity['repoze.who.userid'])
        return groups

    def remember(self, request, principal, **kw):
        """ See IAuthenticationPolicy.
        """

        api_name = decide(request)
        api = self._getAPI(request)
        identity = {'repoze.who.userid': principal,
                    'identifier': api.name_registry[self._identifier_id],
                    'auth_type': api_name,
                   }
        return api.remember(identity)

    def forget(self, request):
        """ See IAuthenticationPolicy.
        """

        api = self._getAPI(request)
        identity = self._get_identity(request)
        return api.forget(identity)

    def _get_groups(self, identity, request):
        if identity is not None:
            if self._callback:
                dynamic = self._callback(identity, request)
                if dynamic is not None:
                    groups = list(dynamic)
                    groups.append(Authenticated)
                    groups.append(Everyone)
                    return groups
        return [Everyone]

    def _getAPI(self, request):
        api_name = decide(request)
        api = who_api(request, api_name)
        return api

    def _get_identity(self, request):
        identity = request.environ.get('repoze.who.identity')
        if identity is None:
            api = self._getAPI(request)
            if api is None:
                return None
            identity = api.authenticate()
        return identity

def includeme(config):
    """
    """
    config.add_directive('add_who_api_factory',
                         add_who_api_factory)
    config.add_directive('set_who_api_decider',
                         set_who_api_decider)
    ini_specs = config.registry.settings.get('altair.auth.specs', "")

    if isinstance(ini_specs, basestring):
        ini_specs = [i.strip() for i in ini_specs.strip().split("\n")
                     if i.strip()]

    for ini_spec in ini_specs:
        if isinstance(ini_spec, basestring):
            if "=" in ini_spec:
                name, ini_file = ini_spec.split("=", 1)
            else:
                name = os.path.splitext(os.path.basename(ini_spec))[0]
                ini_file = ini_spec
        else:
            name, ini_file = ini_spec
        config.add_who_api_factory(name, ini_file)

    decider = config.registry.settings.get('altair.auth.decider')
    if decider:
        config.set_who_api_decider(decider)
    else:
        raise ConfigurationError('altair.auth.decider is not found in settings')

    config.add_tween("altair.auth.activate_who_api_tween", under=INGRESS)

    callback = config.registry.settings.get('altair.auth.callback')
    if callback:
        callback = config.maybe_dotted(callback)

    authentication_policy = MultiWhoAuthenticationPolicy('auth_tkt', callback)
    config.set_authentication_policy(authentication_policy)
    config.add_forbidden_view(ChallengeView)

