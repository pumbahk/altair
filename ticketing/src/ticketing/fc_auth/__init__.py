#
import pyramid.tweens
from repoze.who.api import get_api as get_who_api

class ChallengeView(object):
    def __init__(self, request):
        self.request = request

    def __call__(self):
        who_api = get_who_api(self.request.environ)
        return self.request.get_response(who_api.challenge())

def includeme(config):
    config.add_route('fc_auth.login', '/fc/{membership}/login',
        factory='.resources.FCAuthResource')
    config.add_route('fc_auth.guest', '/fc/{membership}/guest',
        factory='.resources.FCAuthResource')

    config.add_tween('.tweens.FCAuthTween', under=pyramid.tweens.EXCVIEW)
    config.add_static_view('fc_static', 'ticketing.fc_auth:static')
    config.scan('.views')
    config.set_forbidden_view(ChallengeView)
