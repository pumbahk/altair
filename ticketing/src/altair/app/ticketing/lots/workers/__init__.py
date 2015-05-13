# -*- coding: utf-8 -*-
import logging
import transaction
from pyramid.interfaces import IRequest
from ..models import LotEntry
from altair.app.ticketing.models import DBSession

logger = logging.getLogger(__name__)

def on_delivery_error(event):
    import sys
    import traceback
    import StringIO

    e = event.exception
    order = event.order
    exc_info = sys.exc_info()
    out = StringIO.StringIO()
    traceback.print_exception(*exc_info, file=out)
    logger.error(out.getvalue())
    entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==order.order_no).first()
    order.note = str(e)
    if entry is not None:
        entry.order = order
    transaction.commit()


def includeme(config):
    config.include('pyramid_mako')
    config.include('altair.mq')
    config.include('altair.pyramid_dynamic_renderer')
    # payment
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include('altair.app.ticketing.cart.setup_components')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')
    config.include("..sendmail")

    config.add_publisher_consumer('lots.election', 'altair.ticketing.lots.mq')
    config.add_publisher_consumer('lots.rejection', 'altair.ticketing.lots.mq')

    # mail
    config.add_publisher_consumer('lots.election_mail', 'altair.ticketing.lots.mq')
    config.add_publisher_consumer('lots.rejection_mail', 'altair.ticketing.lots.mq')
    config.scan()
