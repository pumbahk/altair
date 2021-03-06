#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pyramid.paster import bootstrap, setup_logging
import StringIO
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime

from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.expression import asc
from webhelpers.number import format_number

import json

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.core.models import Organization, Event, EventSetting, Performance, Product

logger = logging.getLogger(__name__)

charset = locale.getpreferredencoding()
if charset == 'US-ASCII':
    charset = 'utf-8'

datetime_format = "%Y/%m/%d %H:%M"

quiet = False

output = sys.stdout


def set_quiet(q):
    global quiet, output
    if q:
        output = StringIO.StringIO()
    else:
        if quiet:
            print >>sys.stdout, output.getvalue()
            output.close()
        output = sys.stdout
    quiet = q


def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>output, (pad + msg).encode(charset)


def upload(uri, data, resolver):
    key = resolver.resolve(uri).get_key()
    if key:
        headers = {"Content-Type": "application/json"}
        key.set_contents_from_string(json.dumps(data), headers=headers)
        message("upload successfully: %s" % uri)
        key.make_public()
        message("update acl successfully.")
    else:
        set_quiet(False)
        raise Exception("wrong uri: " % uri)


def get_seat_price_from_sales_segment_group_name(group_names, session, seat_price_list, p, now):
    for group_name in group_names:
        sales_segment = get_target_sales_segment(p, now, group_name)
        if not sales_segment:
            message('performance(start=%s, id=%d, name=%s) has no sales_segment(%s)'
                    % (p.start_on, p.id, p.name, group_name.decode('utf-8')))
            continue

        seat_price_list.extend(get_seat_price_list(session, sales_segment))

    return seat_price_list


def get_target_sales_segment(performance, now, sales_segment_group_name):
    sales_segment = [ss for ss in performance.sales_segments if ss.is_not_finished(now) and ss.public
                     and ss.sales_segment_group.name == sales_segment_group_name.decode('utf-8')]
    return sales_segment[0] if sales_segment else None


def get_seat_price_list(session, sales_segment):
    products = session.query(Product) \
        .filter(Product.public == True) \
        .filter(Product.deleted_at == None) \
        .filter(Product.sales_segment_id == sales_segment.id) \
        .order_by(asc(Product.seat_stock_type_id)) \
        .all()

    seat_type_ids = list(set([product.seat_stock_type_id for product in products]))

    seat_price_list = []
    for seat_type_id in seat_type_ids:
        seat_products = [product for product in products if product.seat_stock_type_id == seat_type_id]
        if len(seat_products) > 0:
            seat_price_list.append(
                dict(
                    stock_type_name=seat_products[0].seat_stock_type.name,
                    products=[dict(
                        price=format_number(int(product.price), ','),
                        name=product.name)
                        for product in seat_products]
                )
            )
    return seat_price_list


def output_file(file_name, data):
    file_path = os.path.dirname(file_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(file_name, 'w') as f:
        f.write("%s" % json.dumps(data))


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--target', type=str, required=True)
    parser.add_argument('--quiet', action='store_true', default=False)
    parser.add_argument('--event-id', type=str, default=None)
    parser.add_argument('--sales-segment-group-name', type=str, required=True)
    parser.add_argument('--on-the-day-sales-segment-group-name', type=str, required=True)
    parser.add_argument('--now', type=str, default=None)
    parser.add_argument('--local-run', action='store_true', default=False)
    parser.add_argument('--with-private-performance', action='store_true', default=False)

    opts = parser.parse_args()

    set_quiet(opts.quiet)

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = get_db_session(request, name='slave')
    resolver = get_resolver(env['registry'])

    message('target: %s' % opts.target)
    message('event_id: %s' % opts.event_id)
    message('sales_segment_group_name: %s' % opts.sales_segment_group_name.decode('utf-8'))
    message('on_the_day_sales_segment_group_name: %s' % opts.on_the_day_sales_segment_group_name.decode('utf-8'))
    message('now: %s' % opts.now)
    message('with_private_performance: %s' % opts.with_private_performance)

    try:
        try:
            organization = session.query(Organization) \
                .filter(
                    (Organization.id == opts.organization)
                    | (Organization.short_name == opts.organization)
                    | (Organization.name == opts.organization)
                    | (Organization.code == opts.organization)) \
                .one()
        except NoResultFound:
            set_quiet(False)
            message('No such organization identifiable with %s' % opts.organization)
            return 1
        except MultipleResultsFound:
            set_quiet(False)
            message('Multiple organizations that match to %s' % opts.organization)
            return 1

        now = datetime.strptime(opts.now, '%Y/%m/%d_%H:%M:%S') if opts.now else datetime.now()
        event_ids = map(int, opts.event_id.split(',')) if opts.event_id else []
        sales_segment_group_names = opts.sales_segment_group_name.split(',') if opts.sales_segment_group_name else []
        on_the_day_sales_segment_group_names = opts.on_the_day_sales_segment_group_name.split(',') if opts.on_the_day_sales_segment_group_name else []

        by_start_on = dict()

        query = session.query(Performance) \
            .join(Event, Performance.event_id == Event.id) \
            .join(EventSetting, Event.id == EventSetting.event_id) \
            .filter(Event.organization_id == organization.id) \
            .filter(now.date() <= Performance.start_on) \
            .filter(EventSetting.visible != 0)
        if not opts.with_private_performance:
            query = query.filter(Performance.public != 0)
        if len(event_ids) > 0:
            query = query.filter(Event.id.in_(event_ids))
        performances = query.order_by(Event.display_order, Performance.start_on).all()

        for p in performances:
            if p.start_on not in by_start_on:
                by_start_on[p.start_on] = []
            by_start_on[p.start_on].append(p)

        for start_on, performances in sorted(by_start_on.items()):
            seat_price_list = []

            for p in performances:
                message('performance(start=%s, id=%d, name=%s)' % (p.start_on, p.id, p.name))
                if p.start_on.date() == now.date():
                    seat_price_list = get_seat_price_from_sales_segment_group_name(on_the_day_sales_segment_group_names, session, seat_price_list, p, now)
                else:
                    seat_price_list = get_seat_price_from_sales_segment_group_name(sales_segment_group_names, session, seat_price_list, p, now)

            if len(seat_price_list) > 0:
                if opts.local_run:
                    output_file(os.path.join(opts.target, start_on.strftime('%Y%m%d_%H%M'),
                                             'price.json'), seat_price_list)
                    continue
                upload(opts.target + start_on.strftime('%Y%m%d_%H%M') + '/price.json', seat_price_list, resolver)

    except:
        set_quiet(False)
        raise

    message("done")

    return 0
