# This package may contain traces of nuts
import os
import six
import logging
from pyramid.interfaces import IAuthenticationPolicy, IRequest
from pyramid.security import Everyone, Authenticated
from zope.interface import implementer
from zope.interface.verify import verifyObject
from repoze.who.interfaces import IIdentifier
from .interfaces import IWhoAPIFactoryRegistry, IAugmentedWhoAPIFactory

logger = logging.getLogger(__name__)

REQUEST_KEY = 'altair.auth.request'

from .api import *

@implementer(IAuthenticationPolicy)
class MultiWhoAuthenticationPolicy(object):
    def __init__(self, registry, callback=None):
        self.registry = registry
        self._callback = callback

    def __repr__(self):
        return "{0} callback={1}".format(str(type(self)), str(self._callback))

    @property
    def default_identifier(self):
        return self.registry.queryUtility(IIdentifier, name='altair.auth.default_identifier')

    def unauthenticated_userid(self, request):
        logger.debug('unauthenticated_userid')
        identity = self._get_identity(request)
        if identity is not None:
            return identity['repoze.who.userid']
        return None

    def authenticated_userid(self, request):
        """ See IAuthenticationPolicy.
        """

        identity = self._get_identity(request)

        if identity is not None:
            groups = self._callback(identity, request)
            if groups is not None:
                return identity['repoze.who.userid']
        return None

    def effective_principals(self, request):
        """ See IAuthenticationPolicy.
        """

        identity = self._get_identity(request)
        if identity is None:
            return [Everyone]

        groups = self._get_groups(identity, request)
        if len(groups) > 1:
            groups.insert(0, identity['repoze.who.userid'])
        return groups

    def remember(self, request, principal, **kw):
        """ See IAuthenticationPolicy.
        """

        api, api_name = self._getAPI(request)
        if api is None:
            return []
        identity = {'repoze.who.userid': principal, 'identifier': self.default_identifier, 'altair.auth.type': api_name}
        print identity
        return api.remember(identity)

    def forget(self, request):
        """ See IAuthenticationPolicy.
        """

        api, _ = self._getAPI(request)
        if api is None:
            return []
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
        from .api import who_api
        api, api_name = who_api(request)
        return api, api_name

    def _get_identity(self, request):
        identity = request.environ.get('repoze.who.identity')
        api, name = self._getAPI(request)
        if api is None:
            return None
        if identity is None:
            identity = api.authenticate()
        if identity is not None:
            identity['altair.auth.type'] = name
        return identity

@implementer(IWhoAPIFactoryRegistry)
class WhoAPIFactoryRegistry(object):
    def __init__(self, config):
        self.factories = {}
        self.factories_rev = {}

    def register(self, name, factory):
        logger.debug("%s %s", name, factory)
        verifyObject(IAugmentedWhoAPIFactory, factory)
        self.factories[name] = factory
        self.factories_rev[factory] = name

    def lookup(self, name):
        return self.factories.get(name)

    def reverse_lookup(self, factory):
        return self.factories_rev.get(factory)

    def __iter__(self):
        return six.iteritems(self.factories)


def register_who_api_registry(config):
    config.registry.registerUtility(WhoAPIFactoryRegistry(config))

def register_decider(config):
    decider = config.registry.settings.get('altair.auth.decider')
    if decider:
        config.set_who_api_decider(decider)
    else:
        logger.warning('altair.auth.decider is not found in settings')


def set_auth_policy(config, callback):
    if callback:
        callback = config.maybe_dotted(callback)
    authentication_policy = MultiWhoAuthenticationPolicy(config.registry, callback)
    config.set_authentication_policy(authentication_policy)

def register_auth_policy(config):
    callback = config.registry.settings.get('altair.auth.callback')
    if callback is not None:
        set_auth_policy(config, callback)

def register_default_identifier(config):
    setting_name = 'altair.auth.identifier'
    prefix = setting_name + '.'
    settings = config.registry.settings
    identifier = settings.get(setting_name)
    args = {}
    if identifier is None:
        from .rememberer.pyramid_session import make_plugin
        identifier = make_plugin
    else:
        identifier = config.maybe_dotted(identifier)
        for k in settings:
            if k.startswith(prefix):
                args[k[len(prefix):]] = settings[k]
    config.registry.registerUtility(identifier(**args), IIdentifier, name='altair.auth.default_identifier')

def includeme(config):
    config.include('.config')
    config.include('.activation')
    register_who_api_registry(config)
    register_decider(config)
    register_auth_policy(config)
    register_default_identifier(config)
