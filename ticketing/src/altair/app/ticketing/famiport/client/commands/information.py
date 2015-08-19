# -*- coding: utf-8 -*-
import sys
import argparse
import requests
from pyramid.paster import bootstrap
from pyramid.threadlocal import get_current_request


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--uketsukeCode', default='')
    parser.add_argument('--kogyoSubCode', default='')
    parser.add_argument('--reserveNumber', default='F93BF85534AE0')
    parser.add_argument('--infoKubun', default='1')
    parser.add_argument('--kogyoCode', default='')
    parser.add_argument('--koenCode', default='')
    parser.add_argument('--authCode', default='')
    parser.add_argument('--storeCode', default='000009')
    parser.add_argument('--playGuideId', default='000000000000000000000000')
    args = parser.parse_args(argv)

    bootstrap(args.conf)
    request = get_current_request()

    params = {
        'uketsukeCode': args.uketsukeCode,
        'kogyoSubCode': args.kogyoSubCode,
        'reserveNumber': args.reserveNumber,
        'infoKubun': args.infoKubun,
        'kogyoCode': args.kogyoCode,
        'koenCode': args.koenCode,
        'authCode': args.authCode,
        'storeCode': args.storeCode,
        'playGuideId': args.playGuideId,
        }
    url = request.route_url('famiport.api.reservation.information')
    res = requests.post(url, params=params)
    print(res.content.decode('cp932'))

if __name__ == '__main__':
    main()
