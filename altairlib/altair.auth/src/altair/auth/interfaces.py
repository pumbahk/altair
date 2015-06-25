# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class IWhoAPIDecider(Interface):
    def __call__(request, classification):
        """ 
        :return: str 利用するWho APIの名前
        """

class IPluginRegistry(Interface):
    plugins = Attribute('')

    def register(name, plugin):
        pass

    def lookup(name):
        pass

    def lookup_by_interface(name):
        pass

    def reverse_lookup(plugin):
        pass

    def __iter__(self):
        pass


class IAuthAPI(Interface):
    def authenticate(request, classification, identifier_name=None, identifier_iface=None):
        pass

    def challenge(request, classification, response):
        pass

    def remember(request, classification, response):
        pass

    def forget(request, classification, response):
        pass

    def login(request, classification, response, credentials, identifier_name=None, identifier_iface=None):
        pass

    def logout(request, classification, response, identifier_name=None, identifier_iface=None):
        pass


class IAuthContext(Interface):
    default_identifier = Attribute('')

class IPlugin(Interface):
    name = Attribute('')


class IRequestClassifier(Interface):
    """ On ingress: classify a request.
    """
    def __call__(request):
        """ environ -> request classifier string

        This interface is responsible for returning a string
        value representing a request classification.

        o 'request' is pyramid.request.Request.
        """


class IAuthFactorProvider(IPlugin):
    def get_auth_factors(request, auth_context, credentials=None):
        pass


class ISessionKeeper(IAuthFactorProvider):
    def remember(request, auth_context, response, auth_factors):
        pass

    def forget(request, auth_context, response, auth_factor=None):
        pass


class ILoginHandler(IAuthFactorProvider):
    pass


class IAuthenticator(IPlugin):
    def authenticate(request, auth_context, auth_factors):
        pass


class IChallenger(IPlugin):
    def challenge(request, auth_context, response):
        pass


class IMetadataProvider(IPlugin):
    def get_metadata(request, auth_context, identities):
        pass


class IForbiddenHandler(Interface):
    def __call__(context, request):
        pass
