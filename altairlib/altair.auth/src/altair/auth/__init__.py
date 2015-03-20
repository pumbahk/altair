from __future__ import absolute_import

import os
import six
import logging
from pyramid.response import Response
from zope.interface import implementer
from zope.interface.verify import verifyObject
from .interfaces import (
    IPluginRegistry,
    IPlugin,
    ISessionKeeper,
    IChallenger,
    ILoginHandler,
    IAuthenticator,
    IAuthFactorProvider,
    IMetadataProvider,
    )

logger = logging.getLogger(__name__)

REQUEST_KEY = 'altair.auth.request'

@implementer(IPluginRegistry)
class PluginRegistry(object):
    _interfaces = [
        IAuthFactorProvider,
        ISessionKeeper,
        ILoginHandler,
        IAuthenticator,
        IChallenger,
        IMetadataProvider,
        ]

    def __init__(self, config):
        self._plugins = {}
        self._plugins_by_iface = {}

    def register(self, plugin):
        verifyObject(IPlugin, plugin)
        self._plugins[plugin.name] = plugin
        for iface in self._interfaces:
            plugins_for_iface = self._plugins_by_iface.setdefault(iface, [])
            if iface.providedBy(plugin):
                plugins_for_iface.append(plugin)

    def lookup(self, name):
        return self._plugins.get(name)

    def lookup_by_interface(self, iface):
        return self._plugins_by_iface[iface]        

    @property
    def plugins(self):
        return self._plugins.viewvalues()

    def __iter__(self):
        return six.iteritems(self._plugins)


def register_plugin_registry(config):
    config.registry.registerUtility(PluginRegistry(config))

def register_decider(config, prefix='altair.auth.decider'):
    settings = config.registry.settings
    prefix_with_dot = prefix + '.'
    deciders = []
    for k, v in settings.items():
        if k.startswith(prefix_with_dot):
            classification = k[len(prefix_with_dot):]
            decider = v
            deciders.append((classification, decider))
    decider = settings.get(prefix)
    if decider != None:
        deciders.append((None, decider))
    for classsification, decider in deciders:
        config.set_who_api_decider(decider, classsification) 

def set_auth_policy(config, callback):
    if callback:
        callback = config.maybe_dotted(callback)
    from .pyramid import AuthenticationPolicy
    authentication_policy = AuthenticationPolicy(config.registry, callback)
    config.set_authentication_policy(authentication_policy)

def register_auth_policy(config):
    callback = config.registry.settings.get('altair.auth.callback')
    if callback is not None:
        set_auth_policy(config, callback)

def register_session_keeper(config):
    setting_name = 'altair.auth.session_keeper'
    prefix = setting_name + '.'
    settings = config.registry.settings
    session_keeper = settings.get(setting_name)
    args = {}
    if session_keeper is None:
        from .pyramid import PyramidSessionBasedSessionKeeperPlugin
        session_keeper = PyramidSessionBasedSessionKeeperPlugin
    else:
        session_keeper = config.maybe_dotted(session_keeper)
        for k in settings:
            if k.startswith(prefix):
                args[k[len(prefix):]] = settings[k]
    session_keeper = session_keeper(**args)
    config.registry.registerUtility(session_keeper, ISessionKeeper, name='altair.auth.session_keeper')
    config.registry.queryUtility(IPluginRegistry).register(session_keeper)

def includeme(config):
    config.include('.config')
    register_plugin_registry(config)
    register_decider(config)
    register_auth_policy(config)
    register_session_keeper(config)
    config.add_forbidden_view('.pyramid.challenge_view')
