#

def includeme(config):
    config.add_route('fc_auth.login', '/fc/{membership}/login',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.guest', '/fc/{membership}/guest',
        factory='.resources.FCAuthResource')

    config.add_tween('.tweens.FCAuthTween')
    config.add_static_view('fc_static', 'ticketing.cart.fc_auth:static')
    config.scan('.views')
