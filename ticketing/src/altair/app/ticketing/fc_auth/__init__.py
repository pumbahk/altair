import pyramid.tweens

SESSION_KEY = __name__

def includeme(config):
    config.add_route('fc_auth.login', '/fc/{membership}/login',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.guest', '/fc/{membership}/guest',
        factory='.resources.FCAuthResource')

    #config.add_tween('.tweens.FCAuthTween', under=pyramid.tweens.EXCVIEW)
    config.add_static_view('fc_auth/static', 'altair.app.ticketing.fc_auth:static')
    config.scan('.views')
