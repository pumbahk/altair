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
    parser.add_argument('--ticketingDate', default=now_str)
    parser.add_argument('--orderId', default='123456789012')
    parser.add_argument('--totalAmount', default=1000)
    parser.add_argument('--playGuideId', default='')
    parser.add_argument('--mmkNo', default='01')
    parser.add_argument('--barCodeNo', default='1000000000000')
    parser.add_argument('--sequenceNo', default='15033100010')
    parser.add_argument('--storeCode', default='000009')
    args = parser.parse_args(argv)

    bootstrap(args.conf)
    request = get_current_request()

    params = {
        'ticketingDate': args.ticketingDate,
        'orderId': args.orderId,
        'totalAmount': args.totalAmount,
        'playGuideId': args.playGuideId,
        'mmkNo': args.mmkNo,
        'barCodeNo': args.barCodeNo,
        'sequenceNo': args.sequenceNo,
        'storeCode': args.storeCode,
        }
    url = request.route_url('famiport.api.reservation.completion')
    res = requests.post(url, params=params)
    print(res.content)

if __name__ == '__main__':
    main()
