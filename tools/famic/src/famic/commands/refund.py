# -*- coding: utf-8 -*-
import sys
import datetime
import argparse
import requests
from famic.utils import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    FamiPortRefundAPIURL,
    )


def main(argv=sys.argv[1:]):
    uri = FamiPortRefundAPIURL.REFUND.value
    default_host_port = '{}:{}'.format(DEFAULT_HOST, DEFAULT_PORT)
    parser = argparse.ArgumentParser()

    parser.add_argument('host', default=default_host_port, nargs='?')
    parser.add_argument('--businessFlg', default='3')
    parser.add_argument('--textTyp', default='0')
    parser.add_argument('--entryTyp', default='1')
    parser.add_argument('--shopNo', default='0000001')
    parser.add_argument('--registerNo', default='01')
    parser.add_argument('--barCode', dest='barCode', action='append', nargs='+')
    args = parser.parse_args(argv)

    params = dict(
        businessFlg=args.businessFlg,
        textTyp=args.textTyp,
        entryTyp=args.entryTyp,
        shopNo=args.shopNo,
        registerNo=args.registerNo
        )
    if args.barCode is None:
        parser.error('at least one --barCode option must be specified')
    if len(args.barCode) > 4:
        parser.error('too many --barCode options')
    params.update((k, v) for k, v in zip(['barCode1', 'barCode2', 'barCode3', 'barCode4'], args.barCode))
    host = args.host
    url = '{}://{}/{}'.format(DEFAULT_PROTOCOL, host, uri)
    res = requests.post(url, params=params)
    print(res.content)


if __name__ == '__main__':
    main()

