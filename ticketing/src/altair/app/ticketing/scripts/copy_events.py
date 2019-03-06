#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import transaction
import itertools
import logging
import argparse
import re
import csv
import locale
from datetime import date, datetime, timedelta
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging

from sqlalchemy import func, or_, and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import sqlahelper

from altair.app.ticketing.events.sales_segments.resources import SalesSegmentAccessor

logger = logging.getLogger(__name__)

class ApplicationException(Exception):
    pass

charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

def long2str(n, base, sign='-', digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    retval = ''
    neg = False
    if n < 0:
        n = -n
        neg = True
    while True:
        r = n % base
        n = n // base
        retval += digits[r]
        if n == 0:
            break
    if neg:
        retval += sign
    return retval[::-1]

def generate_event_code(organization, prev_code):
    if prev_code.startswith(organization.code):
        n = long(prev_code[len(organization.code):], 36)
        n += 1
        code = organization.code + long2str(n, 36)
    else:
        n = long(prev_code, 36)
        n += 1
        code = long2str(n, 36)
    return code

def do_event_copy(request, session, event):
    from altair.app.ticketing.core.models import Event, EventSetting
    message(u'Copying Event(id=%ld, code=%s, title=%s)' % (event.id, event.code, event.title))
    new_event = Event(
        code=generate_event_code(event.organization, event.code),
        title=u'%sのコピー' % event.title,
        abbreviated_title=event.abbreviated_title,
        account_id=event.account_id,
        organization_id=event.organization_id,
        display_order=event.display_order,
        setting=EventSetting(
            order_limit=event.setting.order_limit,
            max_quantity_per_user=event.setting.max_quantity_per_user,
            middle_stock_threshold=event.setting.middle_stock_threshold,
            middle_stock_threshold_percent=event.setting.middle_stock_threshold_percent,
            cart_setting_id=event.setting.cart_setting_id
            )
        )
    new_event.original_id = event.id
    new_event.add()

def main(argv=sys.argv):
    from altair.app.ticketing.core.models import Organization, Event
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--organization', metavar='organization', type=str)
    parser.add_argument('event', metavar='event', nargs='+', type=str)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    try:
        organization = None
        try:
            organization = session.query(Organization) \
                .filter(
                    (Organization.id == args.organization) \
                    | (Organization.short_name == args.organization) \
                    | (Organization.name == args.organization) \
                    | (Organization.code == args.organization)) \
                .one()
        except NoResultFound:
            message('No such organization identifiable with %s' % args.organization)
            return 1
        except MultipleResultsFound:
            message('Multiple organizations that match to %s' % args.organization)
            return 1

        try:
            events = []
            for event_id_or_code in args.event:
                try:
                    event = session.query(Event) \
                        .filter(Event.organization_id == organization.id) \
                        .filter(
                            (Event.id == event_id_or_code) \
                            | (Event.code == event_id_or_code)) \
                        .one()
                except NoResultFound:
                    message('No such event identifiable with %s' % event_id_or_code)
                    return 1
                except MultipleResultsFound:
                    message('Multiple events that match to %s' % event_id_or_code)
                    return 1
                events.append(event)

            for event in events:
                do_event_copy(
                    request,
                    session,
                    event
                    )
            transaction.commit()
        except ApplicationException as e:
            message(str(e))
            raise
    except:
        raise
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: sts=4 sw=4 ts=4 et ai
