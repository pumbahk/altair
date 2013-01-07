
from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from ticketing.cart.security import auth_model_callback
from repoze.who.interfaces import IAPIFactory

def includeme(config):
    settings = config.registry.settings
    who_config = settings['pyramid_who.config']
    authentication_policy = WhoV2AuthenticationPolicy(who_config, 'auth_tkt', callback=auth_model_callback)
    config.set_authentication_policy(authentication_policy)
    who_api_factory = authentication_policy._api_factory
    config.registry.registerUtility(who_api_factory, IAPIFactory)
    config.add_tween(".activate_who_api_tween")


def activate_who_api(request):
    registry = request.registry
    factory = registry.getUtility(IAPIFactory)
    api = factory(request.environ)
    request.environ['repoze.who.plugins'] = api.name_registry # BBB?

def activate_who_api_tween(handler, registry):
    def wrap(request):
        activate_who_api(request)
        return handler(request)
    return wrap
