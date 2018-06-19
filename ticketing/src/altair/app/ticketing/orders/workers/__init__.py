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

logger = logging.getLogger(__name__)

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
