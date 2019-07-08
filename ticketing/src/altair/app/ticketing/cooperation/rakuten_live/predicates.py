from altair.app.ticketing.cooperation.rakuten_live.utils import validate_r_live_auth_header
from pyramid.interfaces import IRoutesMapper
from pyramid.urldispatch import Route


class RakutenLiveRequestCorrespondingTo(object):
    """Subscriber Predicates for the R-Live request route matching and Authorization valid"""
    def __init__(self, val, config):
        self.val = (val,) if type(val) is str else val

    def text(self):
        return 'r_live_route = %s' % (self.val,)

    phash = text

    def __call__(self, event):
        """Predicate the request comes from R-Live through the expected route with valid Authorization header."""
        request = event.request

        # matchdict has `route` key when the matching route found from the request.
        # See IRoutesMapper#__call__(request).
        matchdict = request.registry.queryUtility(IRoutesMapper)(request)
        if not matchdict:
            return False

        route = matchdict.get('route')
        if type(route) is not Route or route.name not in self.val:
            return False

        # R-Live request comes with POST method and Authorization header.
        return request.method == 'POST' and validate_r_live_auth_header(request)
