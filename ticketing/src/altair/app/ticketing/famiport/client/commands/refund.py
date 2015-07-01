# -*- coding: utf-8 -*-
import sys
import argparse
import requests
from pyramid.paster import bootstrap
from pyramid.threadlocal import get_current_request


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--businessFlg', default='3')
    parser.add_argument('--textTyp', default='0')
    parser.add_argument('--entryTyp', default='1')
    parser.add_argument('--shopNo', default='0000001')
    parser.add_argument('--registerNo', default='01')
    parser.add_argument('--barCode', dest='barCode', action='append', nargs='+')
    args = parser.parse_args(argv)

    bootstrap(args.conf)
    request = get_current_request()

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

    url = request.route_url('famiport.api.reservation.refund')
    res = requests.post(url, params=params)
    print(res.content)

if __name__ == '__main__':
    main()
