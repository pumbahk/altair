from altair.app.ticketing.cooperation.rakuten_live.utils import is_r_live_referer
from pyramid.interfaces import IRoutesMapper
from pyramid.urldispatch import Route


class RakutenLiveRouteContainedIn(object):
    """Subscriber Predicates for the Request Route matching"""
    def __init__(self, val, config):
        self.val = (val,) if type(val) is str else val

    def text(self):
        return 'r_live_route = %s' % (self.val,)

    phash = text

    def __call__(self, event):
        """Predicate the request comes from R-Live through the expected route."""
        request = event.request

        # Determine R-Live request by HTTP referrer.
        if not is_r_live_referer(request):
            return False

        # matchdict has `route` key when the matching route found from the request.
        # See IRoutesMapper#__call__(request).
        matchdict = request.registry.queryUtility(IRoutesMapper)(request)
        if not matchdict:
            return False

        route = matchdict.get('route')
        return type(route) is Route and route.name in self.val
