#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys
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
    target = opts.target

    try:
        organization = None
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

        performances = session.query(Performance) \
            .join(Event, Performance.event_id==Event.id) \
            .filter(Event.organization_id == organization.id) \
            .all()
        for p in performances:
            if p.start_on < now:
                continue

            stocks = [ ]
            sys.stdout.write("performance start=%s\n" % p.start_on)
            sales_segments = [s for s in p.query_sales_segments(now=now) if s.kind == "normal" ]
            if len(sales_segments) == 1:
                sales_segment = sales_segments[0]

                seat_types = get_seat_type_dicts(request, sales_segment)
                for seat_type in seat_types:
                    stocks.append(dict(name=seat_type["name"], availability=seat_type["availability"]))

                # データ作る
                data = dict(
                    updated_at=now.strftime(format),
                    performance=dict(name=p.name, start_on=p.start_on.strftime(format)),
                    seat_types=stocks,
                )

                # 書き出す
                dst_filename = "%d-%d.json" % (p.id, sales_segment.id)
                sys.stdout.write("filename=%s\n" % dst_filename)
                path = "%s/%s" % (target.strip("/"), dst_filename)

                key = resolver.resolve(path).get_key()
                if key:
                    if opts.dry_run:
                        sys.stdout.write("DRY-RUN: %s\n" % path)
                    else:
                        key.set_contents_from_string(json.dumps(data))
                        sys.stdout.write("upload successfully: %s\n" % path)
                        key.make_public()
                        sys.stdout.write("update acl successfully.\n")
                        key.set_metadata("Content-Type", "application/json")
                        sys.stdout.write("update content-type successfully.\n")
                else:
                    raise
            else:
                sys.stdout.write("skipped (no sales segment with kind=normal).\n")
    except:
        raise
    return 0

    sys.stdout.write("done\n")
    sys.stdout.flush()
