#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import re
from pyramid.paster import bootstrap, setup_logging
import locale
import logging
from argparse import ArgumentParser
from datetime import datetime

import sqlahelper
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import json

from altair.pyramid_assets import get_resolver

from altair.app.ticketing.core.models import Organization, Event, Performance, SalesSegment

from altair.app.ticketing.cart.view_support import get_seat_type_dicts

logger = logging.getLogger(__name__)
charset = locale.getpreferredencoding()

format = "%Y/%m/%d %H:%M"

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

def upload(uri, data, resolver, dry_run):
    key = resolver.resolve(uri).get_key()
    if key:
        if dry_run:
            sys.stdout.write("DRY-RUN: %s\n" % uri)
            sys.stdout.write(json.dumps(data))
        else:
            key.set_contents_from_string(json.dumps(data))
            sys.stdout.write("upload successfully: %s\n" % uri)
            key.make_public()
            sys.stdout.write("update acl successfully.\n")
            key.set_metadata("Content-Type", "application/json")
            sys.stdout.write("update content-type successfully.\n")
    else:
        raise

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
    session = sqlahelper.get_session()
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

        seat_types_index = dict()
        global_data = dict(
            updated_at=now.strftime(format),
            seat_types=[],
            performances=[],
        )

        performances = session.query(Performance) \
            .join(Event, Performance.event_id==Event.id) \
            .filter(Event.organization_id == organization.id) \
            .all()
        for p in performances:
            if p.start_on < now:
                continue

            sys.stdout.write("performance start=%s\n" % p.start_on)
            sales_segments = [s for s in p.query_sales_segments(now=now) if s.kind == "normal" ]
            if len(sales_segments) == 1:
                sales_segment = sales_segments[0]
                seat_types = get_seat_type_dicts(request, sales_segment)

                # 全部入りデータ
                by_name = dict()
                for seat_type in seat_types:
                    if seat_type["name"] not in seat_types_index:
                        seat_types_index[seat_type["name"]] = len(seat_types)
                        global_data["seat_types"].append(seat_type["name"])
                    by_name[seat_type["name"]] = seat_type
                stocks = [by_name[name]["availability"] if (name in by_name) else None for name in seat_types_index]
                global_data["performances"].append(dict(
                    name=p.name,
                    start_on=p.start_on.strftime(format),
                    stocks=stocks,
                ))

                # 個別データ作る
                data = dict(
                    updated_at=now.strftime(format),
                    performance=dict(name=p.name, start_on=p.start_on.strftime(format)),
                    seat_types=[dict(name=s["name"], availability=s["availability"]) for s in seat_types],
                )

                # 個別データ書き出す
                if mode == "each":
                    dst = "%s/%d-%d.json" % (opts.target.strip("/"), p.id, sales_segment.id)
                    upload(dst, data, resolver, opts.dry_run)
            else:
                sys.stdout.write("skipped (no sales segment with kind=normal).\n")

        # 全部入りデータ書き出す
        if mode == "all":
            upload(opts.target, global_data, resolver, opts.dry_run)

    except:
        raise

    sys.stdout.write("done\n")
    sys.stdout.flush()

    return 0
