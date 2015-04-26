from __future__ import absolute_import

import os
import logging
from zope.interface import implementer
from pyramid.interfaces import IRequest
from .interfaces import (
    IWhoAPIDecider,
    IPluginRegistry,
    IAuthAPI,
    IAuthContext,
    IAuthFactorProvider,
    ISessionKeeper,
    IAuthenticator,
    IChallenger,
    ILoginHandler,
    IMetadataProvider,
    IRequestClassifier,
    )

logger = logging.getLogger(__name__)

__all__ = [
    'decide',
    'get_plugin_registry',
    'get_plugins',
    'get_plugin',
    'get_who_api',
    'resolve_plugin_name',
    ]


### stolen from repoze.who
def matches_classification(plugin, iface, classification):
    plugin_classifications = getattr(plugin, 'classifications', {})
    iface_classifications = plugin_classifications.get(iface)
    return not iface_classifications or classification in iface_classifications

@implementer(IAuthAPI, IAuthContext)
class AuthAPI(object):
    def __init__(self, lookup):
        self.lookup = lookup

    def _query_plugins(self, request, base_iface, classification=None, name=None, iface=None, decider=None):
        return [
            plugin
            for plugin in self.lookup(base_iface)
            if (name is None or plugin.name == name) and \
               (iface is None or iface.providedBy(plugin)) and \
               (classification is None or matches_classification(plugin, base_iface, classification)) and \
               (decider is None or decider(request, plugin))
            ]

    @property
    def session_keepers(self):
        return self.lookup(ISessionKeeper)

    def authenticate(self, request, auth_factors=None, classification=None, auth_factor_provider_name=None, auth_factor_provider_iface=None, decider=None):
        if auth_factors is None:
            auth_factors = self._identify(
                request,
                classification=classification,
                base_iface=IAuthFactorProvider,
                name=auth_factor_provider_name,
                iface=auth_factor_provider_iface,
                decider=decider
                )
        return self._authenticate(
            request,
            auth_factors=auth_factors,
            classification=classification,
            decider=decider
            )

    def challenge(self, request, response, classification=None, challenger_name=None, challenger_iface=None, decider=None):
        challengers = self._query_plugins(
            request,
            base_iface=IChallenger,
            classification=classification,
            name=challenger_name,
            iface=challenger_iface,
            decider=decider
            )
        logger.debug('challengers matched for classification "%s": %s' % (classification, challengers))
        for challenger in challengers:
            if challenger.challenge(request, self, response):
                return True
        return False

    def remember(self, request, response, auth_factors=None):
        if auth_factors is None:
            auth_factors = request.environ.get('altair.auth.auth_factors', {})
        for session_keeper in self.lookup(ISessionKeeper):
            auth_factor = auth_factors.get(session_keeper.name)
            if auth_factor is not None:
                session_keeper.remember(request, self, response, auth_factor)

    def forget(self, request, response, auth_factors=None):
        if auth_factors is None:
            auth_factors = request.environ.get('altair.auth.auth_factors', {})
        for session_keeper in self.lookup(ISessionKeeper):
            auth_factor = auth_factors.get(session_keeper.name)
            if auth_factor is not None:
                session_keeper.forget(request, self, response, auth_factor)

    def login(self, request, response, credentials, classification=None, auth_factor_provider_name=None, auth_factor_provider_iface=None, decider=None):
        identities, auth_factors, metadata = self._authenticate(
            request,
            self._identify(
                request,
                credentials=credentials,
                classification=classification,
                base_iface=ILoginHandler,
                name=auth_factor_provider_name,
                iface=auth_factor_provider_iface,
                decider=decider
                ),
            classification=classification,
            decider=decider
            )
        self.remember(request, response, auth_factors)
        return identities, auth_factors, metadata

    def logout(self, request, response, session_keeper_name=None, session_keeper_iface=None, decider=None):
        session_keepers = self._query_plugins(
            request,
            base_iface=ISessionKeeper,
            classification=None,
            name=session_keeper_name,
            iface=session_keeper_iface,
            decider=decider
            )
        for session_keeper in session_keepers:
            session_keeper.forget(request, self, response, None)
        if 'altair.auth.auth_factors' in request.environ:
            auth_factors = request.environ['altair.auth.auth_factors']
            for session_keeper in session_keepers:
                if session_keeper.name in auth_factors:
                    del auth_factors[session_keeper.name]
            if len(auth_factors) == 0:
                del request.environ['altair.auth.auth_factors']
            else:
                # try to reauthenticate with the remaining authentication factors
                return self._authenticate(request, None, auth_factors)

    def _identify(self, request, credentials=None, **criteria):
        auth_factor_providers = self._query_plugins(request, **criteria)
        logger.debug('auth_factor_provider plugins matched for %r: %r' % (criteria, auth_factor_providers))

        results = {}
        for auth_factor_provider in auth_factor_providers:
            auth_factors = auth_factor_provider.get_auth_factors(request, self, credentials)
            if auth_factors is not None:
                logger.debug('auth_factor returned from (auth_factor_provider) %s: %s' % (auth_factor_provider, auth_factors))
                results[auth_factor_provider.name] = auth_factors
            else:
                logger.debug('no auth_factor returned from %s' % (auth_factor_provider,))

        logger.debug('auth factors found: %s' % (results,))
        return results

    def _authenticate(self, request, auth_factors, classification, decider=None):
        authenticators = self._query_plugins(request, IAuthenticator, classification=classification, decider=decider)
        logger.debug('authenticator plugins matched for classification "%s": %s' % (classification, authenticators))

        auth_recs = []

        for authenticator in authenticators:
            identity, filtered_auth_factors = authenticator.authenticate(request, self, auth_factors) 
            if identity is not None:
                logger.debug('identity returned from %s: (identity=%r, filtered_auth_factors=%r)' % (authenticator, identity, filtered_auth_factors))
                rec = dict(
                    authenticator=authenticator,
                    identity=identity,
                    auth_factors=filtered_auth_factors
                    )
                auth_recs.append(rec)
            else:
                logger.debug('no identity returned from %s' % authenticator)

        merged_auth_factors = {}
        identities = {}
        for auth_rec in auth_recs:
            identities[auth_rec['authenticator'].name] = auth_rec['identity']
            for auth_factor_provider_name, auth_factors_for_provider in auth_rec['auth_factors'].items():
                merged_auth_factors.setdefault(auth_factor_provider_name, {}).update(auth_factors_for_provider)
        logger.debug('merged_auth_factors: %r' % merged_auth_factors)
        # allow IMetadataProvider plugins to scribble on the identity
        metadata = self._get_metadata(request, classification, identities)
        request.environ['altair.auth.auth_factors'] = merged_auth_factors
        request.environ['altair.auth.identities'] = identities
        return identities, merged_auth_factors, metadata

    def _get_metadata(self, request, classification, identities):
        """ See IAPI.
        """
        mdproviders = self._query_plugins(request, IMetadataProvider, classification=classification)        
        metadata = {}
        for mdprovider in mdproviders:
            _metadata = mdprovider.get_metadata(request, self, identities)
            if _metadata is not None:
                metadata.update(_metadata)
        return metadata


class AuthAPIAdapter(object):
    def __init__(self, request, api, classification, decider=None):
        self.request = request
        self.api = api
        self.classification = classification
        self.decider = decider

    @property
    def session_keeper(self):
        return self.api.session_keeper

    def authenticate(self, auth_factors=None,identifier_name=None, identifier_iface=None):
        return self.api.authenticate(
            self.request,
            auth_factors=auth_factors,
            classification=self.classification,
            auth_factor_provider_name=identifier_name,
            auth_factor_provider_iface=identifier_iface,
            decider=self.decider
            )

    def challenge(self, challenger_name=None, challenger_iface=None):
        self.api.challenge(
            self.request,
            self.request.response,
            classification=self.classification,
            challenger_name=challenger_name,
            challenger_iface=challenger_iface,
            decider=self.decider
            )
        return self.request.response

    def remember(self, auth_factors=None):
        self.api.remember(self.request, self.request.response, auth_factors)
        return self.request.response

    def forget(self, auth_factors=None):
        self.api.forget(self.request, self.request.response, auth_factors)
        return self.request.response

    def login(self, credentials, auth_factor_provider_name=None, auth_factor_provider_iface=None):
        identities, auth_factors, metadata = self.api.login(
            self.request,
            self.request.response,
            classification=self.classification,
            credentials=credentials,
            auth_factor_provider_name=auth_factor_provider_name,
            auth_factor_provider_iface=auth_factor_provider_iface,
            decider=self.decider
            )
        return identities, auth_factors, metadata, self.request.response

    def logout(self, request, identifier_name=None, identifier_iface=None):
        self.api.logout(self.request, self.request.response, identifier_name, identifier_iface)
        return self.request.response


def decide(request, classification=None):
    decider = request.registry.queryUtility(IWhoAPIDecider, name=classification) \
              if classification is not None \
              else None
    if decider is None:
        decider = request.registry.queryUtility(IWhoAPIDecider) 
    if decider is None:
        return None
    plugin_names = decider(request, classification)
    if isinstance(plugin_names, basestring):
        plugin_names = [plugin_names]
    return plugin_names

def get_plugin_registry(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IPluginRegistry)

def get_plugin(request, name):
    return get_plugin_registry(request).lookup(name)

def get_plugins(request):
    return list(get_plugin_registry(request))

def resolve_plugin_name(request, plugin):
    return get_plugin_registry(request).reverse_lookup(plugin)

def get_request_classifier(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IRequestClassifier)

def get_auth_api(request):
    api = request.environ.get('altair.auth.api')
    if api is not None:
        return api
    registry = get_plugin_registry(request)
    api = AuthAPI(registry.lookup_by_interface)
    request.environ['altair.auth.api'] = api
    return api

def get_who_api(request):
    auth_api = get_auth_api(request)
    adapter = request.environ.get('repoze.who.api')
    if adapter is None:
        request_classifier = get_request_classifier(request)
        if request_classifier is not None:
            classification = request_classifier(request, )
        else:
            classification = None
        def decider(request, plugin):
            if ISessionKeeper.providedBy(plugin):
                return True
            plugin_names = decide(request, classification)
            return plugin.name in plugin_names if plugin_names is not None else True
        adapter = request.environ['repoze.who.api'] = AuthAPIAdapter(request, auth_api, classification, decider)
    return adapter
