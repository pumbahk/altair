#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""購入情報DLのCSVに予約付加属性を追加する
"""
import csv
import sys
import argparse
import itertools
try:
    from unittest import mock
except ImportError:
    import mock  # noqa
from pyramid.paster import (
    bootstrap,
    )
from altair.app.ticketing.famiport.builders import TextFamiPortResponseGenerator
from altair.app.ticketing.famiport.communication.models import FamiPortRefundEntryResponse


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf')
    parser.add_argument('-o', '--output', nargs='?', type=argparse.FileType('w+b'), default=sys.stdout)
    args = parser.parse_args(argv)

    from altair.sqlahelper import get_db_session

    env = bootstrap(args.conf)
    request = env['request']
    session = get_db_session(request, 'famiport')

    for res in session.query(FamiPortRefundEntryResponse).all():
        gen = TextFamiPortResponseGenerator(res)
        txt = gen.serialize(res)
        print(txt)

if __name__ == '__main__':
    main()
