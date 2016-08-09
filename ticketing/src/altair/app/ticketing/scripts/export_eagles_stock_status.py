#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from pyramid.paster import bootstrap, setup_logging
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime

from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import json

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.core.models import Organization, Event, EventSetting, Performance

from altair.app.ticketing.cart.view_support import get_seat_type_dicts

logger = logging.getLogger(__name__)
charset = locale.getpreferredencoding()

datetime_format = "%Y/%m/%d %H:%M"


def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)


def upload(uri, data, resolver, dry_run):
    key = resolver.resolve(uri).get_key()
    if key:
        if dry_run:
            sys.stdout.write("DRY-RUN: %s\n" % uri)
            sys.stdout.write("%s\n" % json.dumps(data))
        else:
            headers = { "Content-Type": "application/json"}
            key.set_contents_from_string(json.dumps(data), headers=headers)
            sys.stdout.write("upload successfully: %s\n" % uri)
            key.make_public()
            sys.stdout.write("update acl successfully.\n")
    else:
        raise


def select_sales_segment(sales_segments):
    sales_segments = [s for s in sales_segments if s.kind == "normal" ]
    if 1 <= len(sales_segments):
        # cart/views.pyによると、単純に[0]を選ぶという戦略で問題ないようだ
        return sales_segments[0]
    return None


def main():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--organization', type=str, required=True)
    parser.add_argument('--target', type=str, required=True)
    parser.add_argument('--dry-run', action='store_true', default=False)

    opts = parser.parse_args()

    setup_logging(opts.config)
    env = bootstrap(opts.config)
    request = env['request']
    session = get_db_session(request, name='slave')
    resolver = get_resolver(env['registry'])

    mode = "all" if re.search(r"\.json$", opts.target) else "each"

    try:
        try:
            organization = session.query(Organization) \
                .filter(
                    (Organization.id == opts.organization) \
                    | (Organization.short_name == opts.organization) \
                    | (Organization.name == opts.organization) \
                    | (Organization.code == opts.organization)) \
                .one()
        except NoResultFound:
            message('No such organization identifiable with %s' % opts.organization)
            return 1
        except MultipleResultsFound:
            message('Multiple organizations that match to %s' % opts.organization)
            return 1

        now = datetime.now()

        global_seat_types = []

        # 初登場のseat type nameだったら、seat_types_indexに登録する
        def register_seat_type(seat_type_name):
            if seat_type_name not in global_seat_types:
                sys.stdout.write("register seat type: %s\n" % seat_type_name)
                global_seat_types.append(seat_type_name)

        by_start_on = dict()

        performances = session.query(Performance) \
            .join(Event, Performance.event_id==Event.id) \
            .join(EventSetting, Event.id==EventSetting.event_id) \
            .filter(Event.organization_id == organization.id) \
            .filter(now <= Performance.start_on) \
            .filter(EventSetting.visible != 0) \
            .filter(Performance.public != 0) \
            .order_by(Event.display_order, Performance.start_on) \
            .all()
        for p in performances:
            sys.stdout.write("performance(start=%s, id=%d, name=%s)\n" % (p.start_on, p.id, p.name))

            sales_segment = p.get_recent_sales_segment(now=now)
            if not sales_segment:
                continue

            seat_types = get_seat_type_dicts(request, sales_segment)

            for seat_type in seat_types:
                register_seat_type(seat_type["name"])

            if p.start_on not in by_start_on:
                by_start_on[p.start_on] = []
            by_start_on[p.start_on].append(dict(
                id=p.id,
                name=p.name,
                event=p.event.title,
                sales_segment=sales_segment.name,
                seat_types=seat_types,
            ))

        global_data = dict(
            updated_at=now.strftime(datetime_format),
            seat_types=global_seat_types,
            performances=[],
        )

        for start_on, performances in sorted(by_start_on.items()):
            sys.stdout.write("start_on=%s\n" % start_on)
            seat_type_by_name = dict()
            for performance in performances:
                sys.stdout.write("  performance(id=%d, event=%s)\n" % (performance["id"], performance["event"]))
                for seat_type in performance["seat_types"]:
                    if seat_type["name"] in seat_type_by_name:
                        sys.stdout.write("*** warn *** found seat type with same name: %s\n" % seat_type["name"])
                        seat_type_by_name[seat_type["name"]].append(seat_type)
                    else:
                        seat_type_by_name[seat_type["name"]] = [ seat_type ]

            def get_availability_by_name(n):
                if n in seat_type_by_name:
                    stock = 0
                    for seat_type in seat_type_by_name[n]:
                        stock = stock + seat_type["availability"]
                    return stock
                else:
                    return None

            global_data["performances"].append(dict(
                start_on=start_on.strftime(datetime_format),
                events=[performance["event"] for performance in performances],
                names=[performance["name"] for performance in performances],
                stocks=[get_availability_by_name(name) for name in global_seat_types],
            ))

            # 個別データ書き出す
            if mode == "each":
                raise Error("not implemented.")

                dst = "%s/%s.json" % (opts.target.strip("/"), start_on.strftime("%Y%m%d-%H%M"))
                data = dict(
                    updated_at=now.strftime(datetime_format),
                    start_on=start_on.strftime(datetime_format),
                    seat_types=[],
                    stocks=[],
                )
                upload(dst, data, resolver, opts.dry_run)

        # 全部入りデータ書き出す
        if mode == "all":
            upload(opts.target, global_data, resolver, opts.dry_run)

    except:
        raise

    sys.stdout.write("done\n")
    sys.stdout.flush()

    return 0
