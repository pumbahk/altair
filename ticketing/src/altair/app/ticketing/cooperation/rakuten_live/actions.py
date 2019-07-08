import logging

from altair.app.ticketing.cooperation.rakuten_live.communicator import RakutenLiveApiCode
from altair.app.ticketing.cooperation.rakuten_live.exceptions import RakutenLiveApiRequestFailed, \
    RakutenLiveApiInternalServerError, RakutenLiveApiAccessTokenInvalid
from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveStatus
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)
_sa_session = scoped_session(sessionmaker(autocommit=True))


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
    _sa_session.add(r_live_request)
    _sa_session.flush()

    if not r_live_request.is_sendable_state:
        return

    try:
        res = communicator.post(data)
    except Exception as e:
        logger.error('[LIV0001] Failed to send a post (RakutenLiveRequest.id={}) to R-Live.'.format(r_live_request.id))
        raise e

    process_r_live_api_result(r_live_request, res)


def process_r_live_api_result(r_live_request, res):
    """Record SENT into RakutenLiveRequest#status or Raise exception if an error response returned."""
    def _msg(reason, content):
        format_message = '[LIV0001] Failed to send a post (RakutenLiveRequest.id={r_live_request_id}) to R-Live. ' \
                         'reason: {reason}, status_code: {status_code} and content: {content}'
        return format_message.format(r_live_request_id=r_live_request.id, reason=reason,
                                     status_code=res.status_code, content=content)

    # R-Live API request always with 200 status code.
    # Code in json response means actual result.
    if res.status_code != 200:
        raise RakutenLiveApiRequestFailed(_msg('Unexpected status code', res.text))

    json_res = res.json()
    code = json_res.get('Code')

    if code == int(RakutenLiveApiCode.SUCCESS):
        # R-Live status changed to SENT only when response is successful
        r_live_request.status = int(RakutenLiveStatus.SENT)
        _sa_session.flush()
    elif code == int(RakutenLiveApiCode.INTERNAL_SERVER_ERROR):
        # Internal Server Error code
        raise RakutenLiveApiInternalServerError(_msg('Internal server error', json_res))
    elif code == int(RakutenLiveApiCode.ACCESS_TOKEN_INVALID):
        # Access token invalid code
        raise RakutenLiveApiAccessTokenInvalid(_msg('Access token invalid', json_res))
    else:
        raise RakutenLiveApiRequestFailed(_msg('Unknown', json_res))
