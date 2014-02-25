class challenge_view_settings(object):
    def __init__(self, route_name):
        self.route_name = route_name

    def __call__(self, wrapped):
        wrapped._challenge_view_settings = {
            'route_name': self.route_name,
            }
        return wrapped
