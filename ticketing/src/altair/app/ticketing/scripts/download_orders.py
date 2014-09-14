#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import json
import argparse

from pyramid.paster import (
    bootstrap,
    setup_logging,
    )

from altair.sqlahelper import get_db_session
from altair.app.ticketing.orders.dump import OrderExporter

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('org', type=int, help='Organization ID')
    parser.add_argument('jsonfile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w+b'), default=sys.stdout)

    opts = parser.parse_args(argv)

    conf_path = opts.conf
    organization_id = opts.org
    json_str = opts.jsonfile.read()
    outputfp = opts.output

    data = json.loads(json_str)
    filters = data['filters']
    options = data['options']
    limit = data['limit']

    setup_logging(conf_path)
    env = bootstrap(conf_path)
    request = env['request']

    session = get_db_session(request, name='slave')
    exporter = OrderExporter(session, organization_id)
    exporter.exportfp(outputfp, filters=filters, options=options, limit=limit)

if __name__ == '__main__':
    main()
