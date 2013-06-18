# -*- encoding:utf-8 -*-

"""
csvのformat

organization_id, operator_id, title, filename
"""
import sys
import csv
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
import transaction
from pyramid.paster import bootstrap

def main():
    parser = argparse.ArgumentParser(description="register category top page", formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("config", help=u"development.ini'")
    parser.add_argument('infile', help=u"csv file", nargs='?', type=argparse.FileType('r'), 
                        default=sys.stdin)
    parser.add_argument('prefix', help=u"csv file", nargs='?', default=".")
    parser.add_argument("--verbose", default=False, action="store_const", const=bool)
    args = parser.parse_args()
    _main(args)

def _main(args):
    try:
        env = bootstrap(args.config)
        run(env, args.infile, args.prefix)
        transaction.commit()
    except Exception, e:
        logger.exception(str(e))
        transaction.abort()

def get(qs):
    return qs.one()

import os.path

def run(env, csvfile, prefix):
    from altaircms.asset.resources import AssetResource
    from altaircms.asset.views import AssetCreateView
    from altaircms.testing import ExtDummyRequest
    from altaircms.testing import DummyFileStorage
    for organization_id, operator_id, title, filename in csv.reader(csvfile):
        filename = os.path.join(prefix, filename.strip())
        if not os.path.exists(filename):
            logger.warn("skip: title %s filename %s organization %s" % (title, filename, organization_id))
            continue
        params = dict(
            title = title, 
            filepath = DummyFileStorage(filename, file=filename)
            )
        request = ExtDummyRequest(organization_id=organization_id, operator_id=operator_id, 
                                  POST=params, current_request=True)
        context = AssetResource(request)
        try:
            view = AssetCreateView(context, request)
            view.create_image_asset()
            sys.stderr.write(".")
        except:
            logger.warn("error: title %s filename %s organization %s" % (title, filename, organization_id))

if __name__ == "__main__":
    main()
