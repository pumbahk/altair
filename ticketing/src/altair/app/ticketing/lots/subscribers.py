import logging
from datetime import datetime
from pyramid.events import subscriber
#from . import api
from . import sendmail
from altair.multicheckout.models import MultiCheckoutOrderStatus
from altair.multicheckout.api import get_multicheckout_3d_api
from altair.now import get_now

logger = logging.getLogger(__name__)

@subscriber('altair.app.ticketing.lots.events.LotEntriedEvent')
def send_lot_accepted_mail(event):
    entry = event.lot_entry
    request = event.request
    sendmail.send_accepted_mail(request, entry)


@subscriber('altair.app.ticketing.lots.events.LotElectedEvent')
def finish_elected_lot_entry(event):
    try:
        entry = event.lot_entry
        if entry.ordered_mail_sent_at:
            return
        wish = event.lot_wish
        request = event.request
        sendmail.send_elected_mail(request, entry, wish)
        entry.ordered_mail_sent_at = get_now(request)
    except Exception as e:
        logger.exception(e)

@subscriber('altair.app.ticketing.lots.events.LotRejectedEvent')
def finish_rejected_lot_entry(event):
    try:
        entry = event.lot_entry

        request = event.request
        sendmail.send_rejected_mail(request, entry)
        entry.ordered_mail_sent_at = get_now(request)
    except Exception as e:
        logger.exception(e)


@subscriber('altair.app.ticketing.lots.events.LotClosedEvent')
def finish_closed_lot_entry(event):
    try:
        entry = event.lot_entry
        request = event.request
        multicheckout_api = get_multicheckout_3d_api(
            request,
            override_name=entry.lot.event.organization.setting.multicheckout_shop_name
            )
        multicheckout_api.keep_authorization(entry.entry_no, None)
    except Exception as e:
        logger.exception(e)

def includeme(config):
    config.scan('.subscribers')
