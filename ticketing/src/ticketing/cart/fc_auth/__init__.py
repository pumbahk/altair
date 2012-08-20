#

def includeme(config):
    config.add_route('fc_auth.login', '/fc/{membership}/login',
        factory='.resources.FCAuthResource')

    config.add_tween('.tweens.FCAuthTween')
    config.scan('.views')
