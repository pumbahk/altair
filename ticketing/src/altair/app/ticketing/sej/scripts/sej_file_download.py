# -*- coding:utf-8 -*-

#
# 通知ファイルをダウンロードする
#

import sys
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound
import argparse, textwrap

from os.path import abspath, dirname

from pyramid.paster import bootstrap
from ..payment import request_fileget
from ..models import (
    SejTenant,
    SejNotificationType,
    code_from_notification_type
    )
from ..exceptions import SejServerError

from dateutil.parser import parse as parsedate

from paste.deploy import loadapp

import logging

log = logging.getLogger(__file__)

import os

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

    shop_id = registry.settings.get('altair.sej.shop_id') or registry.settings.get('sej.shop_id')
    api_key = registry.settings.get('altair.sej.api_key') or registry.settings.get('sej.api_key')
    api_url = registry.settings.get('altair.sej.inticket_api_url') or registry.settings.get('sej.inticket_api_url')
    if args.organization:
        tenant = SejTenant.query.filter_by(organization_id=args.organization).one()
        if tenant.shop_id: shop_id = tenant.shop_id
        if tenant.api_key: api_key = tenant.api_key
        if tenant.inticket_api_url: api_url = tenant.inticket_api_url
    if args.shop_id: shop_id = args.shop_id
    if args.apikey: api_key = args.apikey
    if args.endpoint: api_url = args.endpoint

    if not (shop_id and api_key and api_url):
        print >>sys.stderr, "could not determine either shop_id, api_key or api_url"
        return 1

    for date in args.date:
        body = request_fileget(
            args.type,
            parsedate(date),
            shop_id=shop_id,
            secret_key=api_key,
            hostname=api_url,
            )
        sys.stdout.write(body)
        sys.stdout.flush()

if __name__ == u"__main__":
    logging.basicConfig()
    sys.exit(main(sys.argv))
