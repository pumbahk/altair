# -*- coding:utf-8 -*-

#
# 通知ファイルをダウンロードする
#

import os
import sys
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound
import argparse, textwrap

from os.path import abspath, dirname

from pyramid.paster import bootstrap
from ..payment import request_fileget
from ..models import (
    SejNotificationType,
    ThinSejTenant,
    code_from_notification_type
    )
from ..api import validate_sej_tenant
from ...core.models import SejTenant
from ..exceptions import SejServerError

from dateutil.parser import parse as parsedate

from paste.deploy import loadapp

import logging


log = logging.getLogger(__file__)

DBSession = sqlahelper.get_session()

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('date', metavar='YYYYMMDD', type=str, nargs='*',
                        help="target date")
    parser.add_argument('-O', '--organization', metavar='organization', type=long,
                        help='organization name')
    parser.add_argument('-u', '--endpoint', metavar='endpoint', type=str,
                        help='api endpoint')
    parser.add_argument('-s', '--shop-id', metavar='shopid', type=str,
                        help='shopid')
    parser.add_argument('-k', '--apikey', metavar='apikey', type=str,
                        help='api key')
    parser.add_argument('-t', '--type', metavar='tuchi_kbn', type=int,
                        required=True, help=u"通知区分")

    args = parser.parse_args()

    env = bootstrap(args.config_uri)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    session = sqlahelper.get_session()
    session.configure(autocommit=True, extension=[])

    if args.organization:
        from altair.app.ticketing.sej import userside_api
        tenant = userside_api.lookup_sej_tenant(request, args.organization)
    else:
        tenant = get_default_sej_tenant()

    tenant = ThinSejTenant(
        original=tenant,
        shop_id=args.shop_id,
        api_key=args.apikey,
        inticket_api_url=args.endpoint
        )

    try:
        validate_sej_tenant(tenant)
    except AssertionError as e:
        print >>sys.stderr, str(e)
        return 1

    for date in args.date:
        body = request_fileget(
            args.type,
            parsedate(date),
            tenant=tenant
            )
        sys.stdout.write(body)
        sys.stdout.flush()

if __name__ == u"__main__":
    logging.basicConfig()
    sys.exit(main(sys.argv))
