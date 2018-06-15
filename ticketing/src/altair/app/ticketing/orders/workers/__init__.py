# -*- coding: utf-8 -*-
import logging
import transaction
from pyramid.interfaces import IRequest

from altair.app.ticketing.cart.carting import CartFactory
from altair.app.ticketing.cart.interfaces import (IStocker,
                                                  IReserving,
                                                  ICartFactory)
from altair.app.ticketing.cart.reserving import Reserving
from altair.app.ticketing.cart.stocker import Stocker
from ..models import ProtoOrder, Order, OrderImportTask
from altair.app.ticketing.models import DBSession

logger = logging.getLogger(__name__)

def on_delivery_error(event):
    # import sys
    # import traceback
    # import StringIO
    #
    # e = event.exception
    # order = event.order
    # exc_info = sys.exc_info()
    # out = StringIO.StringIO()
    # traceback.print_exception(*exc_info, file=out)
    # logger.error(out.getvalue())
    # entry = DBSession.query(LotEntry).filter(LotEntry.entry_no==order.order_no).first()
    # order.note = str(e)
    # if entry is not None:
    #     entry.order = order
    # transaction.commit()
    pass

def setup_components(config):

    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)

def includeme(config):
    # mq
    config.include('altair.mq')
    # payment
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include(setup_components)

    config.add_publisher_consumer('import_per_order', 'altair.ticketing.orders.mq')
    config.add_publisher_consumer('import_per_task', 'altair.ticketing.orders.mq')

    config.scan()
