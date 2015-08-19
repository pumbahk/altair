# -*- coding:utf-8 -*-

import argparse
import sys
import os
import json
import logging
from datetime import date
from decimal import Decimal
from ..accounting.sales_report import make_unmarshaller

logger = logging.getLogger(__name__)

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, Decimal):
            return unicode(o.quantize(0))
        else:
            try:
                i = iter(o)
                return listwrap(i)
            except TypeError:
                raise super(MyJSONEncoder, self).default(o)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--eor', help='eor', type=str, default='\\r\\n')
    parser.add_argument('--encoding', type=str, help='encoding', default='CP932')
    parser.add_argument('file', metavar='file', type=str, help='file')
    args = parser.parse_args(argv[1:])
    eor = args.eor.decode('string_escape')
    encoding = args.encoding
    with open(args.file) as f:
        for x in make_unmarshaller(f, encoding=encoding, eor=eor):
            print MyJSONEncoder(ensure_ascii=False, indent=True).encode(x)

if __name__ == u"__main__":
    main(sys.argv)
