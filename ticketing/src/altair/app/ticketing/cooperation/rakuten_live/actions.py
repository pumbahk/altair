import logging

from sqlalchemy.orm import scoped_session, sessionmaker

from altair.app.ticketing.cooperation.rakuten_live.exceptions import RakutenLiveCommunicationFailed
from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession, RakutenLiveStatus
from altair.app.ticketing.cooperation.rakuten_live.utils import validate_authorization_header
from pyramid.interfaces import IRoutesMapper
from pyramid.urldispatch import Route

logger = logging.getLogger(__name__)
_sa_session = scoped_session(sessionmaker(autocommit=True))


def store_r_live_request_param(request, registry=None):
    """Store R-Live request param in session.
    """
    registry = registry or request.registry

    # R-Live request comes with POST method and Authorization header.
    if not request.referer or \
            not request.referer.startswith(registry.settings.get('r-live.referer')) or \
            not validate_authorization_header(request, registry) or \
            request.method != 'POST':
        return

    # matchdict has `route` key when the matching route found from the request.
    # See IRoutesMapper#__call__(request).
    matchdict = registry.queryUtility(IRoutesMapper)(request)
    if not matchdict or type(matchdict.get('route')) is not Route:
        return

    # Request params stored in session when the request comes through the expected route.
    from . import R_LIVE_REQUEST_ROUTES
    if matchdict.get('route').name not in R_LIVE_REQUEST_ROUTES:
        return

    req_dict = request.POST
    # matchdict has `match` key, containing matched route's pattern.
    # performance_id and lot_id should be included because any expected route from R-Live contains either of them.
    req_dict.update(matchdict.get('match', {}))

    session_key = registry.settings.get('r-live.session_key')
    request.session[session_key] = RakutenLiveSession(**req_dict)


def build_r_live_order_data(order, r_live_session):
    data = r_live_session.as_dict()
    data.update({
        'order_no': order.order_no,
        'concert_name': order.performance.name,
        'is_order': True,
        'products': [
            {
                'name': ordered_product.product.name,
                'number_of_items': ordered_product.seat_quantity,
                'unit_price': ordered_product.price
            } for ordered_product in order.ordered_products
        ],
        'total_price': order.total_amount,
        'currency': 'JPY'
    })
    return data


def build_r_live_entry_data(entry, r_live_session):
    # LotEntry could have multiple choices (LotEntryWish), but only first choice's data is sent.
    first_wish = None
    for w in entry.wishes:
        if w.wish_order == 0:
            first_wish = w
            break

    data = r_live_session.as_dict()
    data.update({
        'order_no': entry.entry_no,
        'concert_name': first_wish.performance.name,
        'is_order': False,
        'products': [
            {
                'name': lot_product.product.name,
                'number_of_items': lot_product.quantity,
                'unit_price': lot_product.subtotal
            } for lot_product in first_wish.products
        ],
        'total_price': first_wish.total_amount,
        'currency': 'JPY'
    })
    return data


def send_r_live_data(communicator, data, r_live_session, order_entry_no):
    """Send Order or LotEntry data to R-Live and Record status of the communication result."""
    r_live_request = r_live_session.as_model(order_entry_no=order_entry_no)
    _sa_session.merge(r_live_request)
    _sa_session.flush()

    if not r_live_request.is_sendable_state:
        return

    try:
        res = communicator.post(data)
    except Exception as e:
        logger.error('[LIV0001] Failed to send a post (RakutenLiveRequest.id={}) to R-Live.'.format(r_live_request.id))
        raise e

    if res.ok:
        r_live_request.status = int(RakutenLiveStatus.SENT)
        _sa_session.merge(r_live_request)
        _sa_session.flush()
    else:
        logger.error('[LIV0001] Failed to send a post (RakutenLiveRequest.id={}) to R-Live. '
                     'Response status code: {} and content: {}'.format(r_live_request.id, res.status_code, res.content))
        raise RakutenLiveCommunicationFailed('Error response has returned.')
