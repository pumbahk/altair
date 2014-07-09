# -*- coding:utf-8 -*-

#
# 通知ファイルをダウンロードする
#

import os
import sys
import time
import codecs
import sqlahelper
import logging
import argparse
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging

from ..payment import request_fileget
from ..models import ThinSejTenant
from ..api import validate_sej_tenant, get_default_sej_tenant

logger = logging.getLogger(__name__)


def get_download_filename(date):
    return '{0}_{1}.dat'.format(date, int(time.time()))

def download(request, organization, shop_id, apikey, endpoint, type, dates, out_dir=None):
    if organization:
        from altair.app.ticketing.sej import userside_api
        tenant = userside_api.lookup_sej_tenant(request, organization)
    else:
        tenant = get_default_sej_tenant(request)

    tenant = ThinSejTenant(
        original=tenant,
        shop_id=shop_id,
        api_key=apikey,
        inticket_api_url=endpoint
        )

    try:
        validate_sej_tenant(tenant)
    except AssertionError as e:
        logger.exception(e)
        raise

    files = []
    for date in dates:
        body = request_fileget(
            request,
            tenant=tenant,
            notification_type=type,
            date=parsedate(date)
            )

        if out_dir is not None:
            file_name = os.path.join(out_dir, get_download_filename(date))
            in_file = codecs.open(file_name, 'w', 'CP932')
            in_file.write(body)
            in_file.close()
            files.append(file_name)
        else:
            sys.stdout.write(body)
            sys.stdout.flush()
    return files

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

    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']

    try:
        download(request,
                 args.organization,
                 args.shop_id,
                 args.apikey,
                 args.endpoint,
                 args.type,
                 args.date)
    except Exception as e:
        logger.exception(e)
        return 1
    return 0


if __name__ == u"__main__":
    sys.exit(main(sys.argv))
