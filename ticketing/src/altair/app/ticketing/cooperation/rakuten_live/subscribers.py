from pyramid.events import subscriber, NewRequest
from pyramid.interfaces import IRoutesMapper

from altair.app.ticketing.cooperation.rakuten_live import R_LIVE_REQUEST_ROUTES
from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession


@subscriber(NewRequest, r_live_route=R_LIVE_REQUEST_ROUTES)
def r_live_session_store_subscriber(event):
    """
    Store request params in a session for R-Live credentials.
    """
    request = event.request
    credentials = {}
    credentials.update(request.POST or {})

    # See IRoutesMapper#__call__(request).
    matchdict = request.registry.queryUtility(IRoutesMapper)(request)

    # matchdict has `match` key, containing matched route's pattern.
    # performance_id and lot_id should be included because any expected route from R-Live contains either of them.
    credentials.update(matchdict.get('match', {}))

    session_key = request.registry.settings.get('r-live.session_key')
    request.session[session_key] = RakutenLiveSession(**credentials)
