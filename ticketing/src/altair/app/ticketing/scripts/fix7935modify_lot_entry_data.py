#-*- coding: utf-8 -*-
#!/usr/bin/env python
import argparse
import csv
import sys

import transaction
from altair.app.ticketing.core.models import DBSession
from altair.app.ticketing.lots.models import LotEntry
from pyramid.paster import bootstrap


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('--file_name', metavar='file_name', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']
    import sys
    print(sys.version)
    with open(args.file_name, 'r') as f:
        reader = csv.reader(f)

        for row in reader:
            entry_no = row[0]
            entry = LotEntry.query.filter(LotEntry.entry_no == entry_no).first()
            entry.wishes[0].products[0].product_id = row[1]
            DBSession.flush()

    transaction.commit()


if __name__ == '__main__':
    main()
