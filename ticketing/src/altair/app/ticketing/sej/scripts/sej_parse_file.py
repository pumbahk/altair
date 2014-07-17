# -*- coding:utf-8 -*-

#
# 通知ファイルをパースしてCSV化する
#

import os
import sys
import argparse
import csv
import logging

from pyramid.paster import bootstrap, setup_logging

from ..file import parsers, SejFileReader

logger = logging.getLogger(__name__)


def record_coerce(v):
    if v is None:
        return u''
    if isinstance(v, unicode):
        return v
    return unicode(v)

def process_files(type, files, in_encoding='CP932', out_encoding='CP932'):
    parser_map = dict(
        (notification_type.v, parser)
        for parser in parsers
        for notification_type in parser.notification_types
        )

    parser_factory = parser_map.get(type)
    if parser_factory is None:
        logger.error("Unknown notification type: %d" % type)
        logger.error("where supported: %s" % ", ".join(str(i) for i in parser_map.keys()))
        return 1

    def process_one_file(in_file_name=None):
        if in_file_name is None:
            in_file = sys.stdin
            out_dir = ''
        else:
            in_file = open(in_file_name)
            out_dir = os.path.abspath(os.path.dirname(in_file_name))

        while True:
            parser = parser_factory(SejFileReader(in_file, encoding=in_encoding))
            if not parser.parse():
                break
            out_file_name = parser.filename.replace('/', '_').replace(os.path.sep, ')') + '.csv'
            out_file_name = os.path.join(out_dir, out_file_name)
            logger.info("Writing records to %s..." % out_file_name)

            f = open(out_file_name, 'w')
            try:
                w = csv.writer(f)
                if len(parser.records) > 0:
                    headers = parser.records[0].keys()
                    w.writerow([k.encode(out_encoding) for k in headers])
                    for record in parser.records:
                        w.writerow([record_coerce(record[k]).encode(out_encoding) for k in headers])
            finally:
                f.close()

    if not files:
        process_one_file()
    else:
        for file in files:
            process_one_file(file)

    return

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

    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    process_files(type=args.type,
                  files=args.file,
                  in_encoding=args.in_encoding,
                  out_encoding=args.out_encoding)


if __name__ == u"__main__":
    sys.exit(main(sys.argv))
