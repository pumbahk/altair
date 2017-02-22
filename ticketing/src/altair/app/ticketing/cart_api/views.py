from pyramid.view import view_defaults, view_config


@view_defaults(renderer='json')
class APIView(object):
    def __init__(self, context, request):
         self.context = context
         self.request = request

    @view_config(route_name='cart.api.index')
    def index(self):
        return dict(status='OK')
