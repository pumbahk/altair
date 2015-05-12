import logging
from datetime import datetime, timedelta
from pyramid.events import subscriber
from . import sendmail
from altair.multicheckout.models import MultiCheckoutOrderStatus
from altair.multicheckout.api import get_multicheckout_3d_api
from altair.now import get_now
from altair.timeparse import parse_time_spec

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
        if entry.ordered_mail_sent_at:
            return
        request = event.request
        sendmail.send_rejected_mail(request, entry)
        entry.ordered_mail_sent_at = get_now(request)
    except Exception as e:
        logger.exception(e)


class LotEntryCloser(object):
    def __init__(self, registry):
        self.registry = registry
        moratorium = registry.settings.get('lots.election.pending_sales_cancel_moratorium', None)
        if moratorium is None:
            moratorium = timedelta(hours=1)
        else:
            moratorium = parse_time_spec(moratorium)
        self.moratorium = moratorium

    def __call__(self, event):
        now = datetime.now()
        try:
            entry = event.lot_entry
            request = event.request
            multicheckout_api = get_multicheckout_3d_api(
                request,
                override_name=entry.lot.event.organization.setting.multicheckout_shop_name
                )
            status = multicheckout_api.get_order_status_by_order_no(entry.entry_no)
            if status is not None:
                if status.is_authorized:
                    multicheckout_api.keep_authorization(entry.entry_no, None)
                elif status.is_settled:
                    multicheckout_api.schedule_cancellation(entry.entry_no, now + self.moratorium, 0, 0)
        except Exception as e:
            logger.exception(e)

def includeme(config):
    config.scan('.subscribers')
    config.add_subscriber(LotEntryCloser(config.registry), '.events.LotClosedEvent')
