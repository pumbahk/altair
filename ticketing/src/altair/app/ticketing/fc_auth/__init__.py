import pyramid.tweens

SESSION_KEY = __name__

def register_auth_plugin(config):
    from .plugins import FCAuthPlugin
    fc_auth = FCAuthPlugin()
    config.add_auth_plugin(fc_auth)

def setup_routes(config):
    config.add_route(
        'fc_auth.login',
        '/fc/{membership}/login',
        factory='.resources.fc_auth_resource_factory'
        )
    config.add_route(
        'fc_auth.guest',
        '/fc/{membership}/guest',
        factory='.resources.fc_auth_resource_factory'
        )

def includeme(config):
    config.include(setup_routes)
    config.include('.rendering')
    config.scan('.views')

    config.add_static_view('fc_auth/static', 'altair.app.ticketing.fc_auth:static')
    config.include(register_auth_plugin)
