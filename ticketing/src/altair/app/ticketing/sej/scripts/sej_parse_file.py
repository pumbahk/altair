# -*- coding:utf-8 -*-

#
# 通知ファイルをパースしてCSV化する
#

import sys
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound
import argparse
import csv

from pyramid.paster import bootstrap
from ..resources import SejNotificationType
from ..exceptions import SejServerError
from ..file import parsers, SejFileReader

from dateutil.parser import parse as parsedate

from paste.deploy import loadapp

import logging

log = logging.getLogger(__file__)

import os

def record_coerce(v):
    if v is None:
        return u''
    if isinstance(v, unicode):
        return v
    return unicode(v)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('file', metavar='file', type=str, nargs='*',
                        help='file')
    parser.add_argument('--out-encoding', metavar='out_encoding', type=str,
                        help='output file encoding', default='CP932')
    parser.add_argument('--in-encoding', metavar='in_encoding', type=str,
                        help='input file encoding', default='CP932')
    parser.add_argument('-t', '--type', metavar='tuchi_kbn', type=int,
                        required=True, help=u"通知区分")

    args = parser.parse_args()

    env = bootstrap(args.config_uri)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    parser_map = dict(
        (notification_type.v, parser)
        for parser in parsers
        for notification_type in parser.notification_types
        )

    parser_factory = parser_map.get(args.type)
    if parser_factory is None:
        print >>sys.stderr, "Unknown notification type: %d" % args.type
        print >>sys.stderr, "where supported: %s" % ", ".join(str(i) for i in parser_map.keys())
        return 1

    def process_one_file(in_file):
        while True:
            parser = parser_factory(SejFileReader(in_file, encoding=args.in_encoding))
            if not parser.parse():
                break
            out_file_name = parser.filename.replace('/', '_').replace(os.path.sep, ')') + '.csv'
            print >>sys.stderr, "Writing records to %s..." % out_file_name,
            f = open(out_file_name, 'w')
            try:
                w = csv.writer(f)

                if len(parser.records) > 0:
                    headers = parser.records[0].keys()
                    w.writerow([k.encode(args.out_encoding) for k in headers])
                    for record in parser.records:
                        w.writerow([record_coerce(record[k]).encode(args.out_encoding) for k in headers])
            finally:
                f.close()
            print "done"

    if not args.file:
        process_one_file(sys.stdin)
    else:
        for file in args.file:
            process_one_file(open(file))

if __name__ == u"__main__":
    logging.basicConfig()
    sys.exit(main(sys.argv))
