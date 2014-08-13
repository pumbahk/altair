import pyramid.tweens

SESSION_KEY = __name__

def register_auth_plugin(config):
    from altair.auth.facade import AugmentedWhoAPIFactory
    from repoze.who.classifiers import default_request_classifier
    from .plugins import FCAuthPlugin
    fc_auth = FCAuthPlugin()
    config.add_who_api_factory(
        'fc_auth',
        AugmentedWhoAPIFactory(
            authenticators=[('fc_auth', fc_auth)],
            challengers=[('fc_auth', fc_auth)],
            mdproviders=[('fc_auth', fc_auth)],
            request_classifier=default_request_classifier
            )
        )

def includeme(config):
    config.add_route('fc_auth.login', '/fc/{membership}/login',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.guest', '/fc/{membership}/guest',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.detail_login', '/fc/{membership}/{detail_membership}/login',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.detail_guest', '/fc/{membership}/{detail_membership}/guest',
        factory='.resources.FCAuthResource')

    config.add_static_view('fc_auth/static', 'altair.app.ticketing.fc_auth:static')
    config.scan('.views')
    register_auth_plugin(config)
