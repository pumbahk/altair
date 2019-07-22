from altair.app.ticketing.cooperation.rakuten_live.utils import validate_r_live_auth_header
from pyramid.interfaces import IRoutesMapper
from pyramid.urldispatch import Route


class RakutenLiveRequestRouteAuthorized(object):
    """Subscriber Predicates for the R-Live request method, authorization header and routes."""
    def __init__(self, val, config):
        self.val = (val,) if type(val) is str else val

    def text(self):
        return 'r_live_route = %s' % (self.val,)

    phash = text

    def __call__(self, event):
        """Predicate the request comes from R-Live through the expected route with valid Authorization header."""
        request = event.request
        # R-Live request comes with POST method and Authorization header.
        if request.method != 'POST' or not validate_r_live_auth_header(request):
            return False

        # matchdict has `route` key when the matching route found from the request.
        # See IRoutesMapper#__call__(request).
        matchdict = request.registry.queryUtility(IRoutesMapper)(request)
        if not matchdict:
            return False

        route = matchdict.get('route')
        return type(route) is Route and route.name in self.val
