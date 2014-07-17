#-*- coding: utf-8 -*-
import sys
import time
import argparse
import datetime
try:
    import stringio
except ImportError:
    import StringIO as stringio
import pyramid.request
import pyramid.paster
import pyramid.testing
import transaction
import mako.template
import altair.sqlahelper
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import (
    Event,
    Performance,
    PaymentMethod,
    DeliveryMethod,
    PaymentDeliveryMethodPair,
    )
from altair.app.ticketing.orders.models import Order

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf')
    opts = parser.parse_args(argv)

    pyramid.paster.setup_logging(opts.conf)
    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings
    request = pyramid.testing.DummyRequest()
    session = altair.sqlahelper.get_db_session(request, 'slave')

if __name__ == '__main__':
    main()
