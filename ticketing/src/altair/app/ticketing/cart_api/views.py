from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPNotFound

@view_defaults(renderer='json')
class CartAPIView(object):
    def __init__(self, context, request):
         self.context = context
         self.request = request

    @view_config(route_name='cart.api.health_check')
    def health_check(self):
        return HTTPNotFound()

    @view_config(route_name='cart.api.index')
    def index(self):
        return dict(status='OK')
