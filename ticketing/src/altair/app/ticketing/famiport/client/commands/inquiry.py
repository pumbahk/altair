# -*- coding: utf-8 -*-
import sys
import datetime
import argparse
import requests
from pyramid.paster import bootstrap
from pyramid.threadlocal import get_current_request


def main(argv=sys.argv[1:]):
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--authNumber', default='')
    parser.add_argument('--reserveNumber', default='5300000000001')
    parser.add_argument('--ticketingDate', default=now_str)
    parser.add_argument('--storeCode', default='000009')
    args = parser.parse_args(argv)

    bootstrap(args.conf)
    request = get_current_request()

    params = {
        'authNumber': args.authNumber,
        'reserveNumber': args.reserveNumber,
        'ticketingDate': args.ticketingDate,
        'storeCode': args.storeCode,
        }
    url = request.route_url('famiport.api.reservation.inquiry')
    res = requests.post(url, params=params)
    print(res.content)


if __name__ == '__main__':
    main()
