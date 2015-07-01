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
    parser.add_argument('--orderId', default='410900000005')
    parser.add_argument('--totalAmount', default=2200)
    parser.add_argument('--playGuideId', default='02')
    parser.add_argument('--mmkNo', default='01')
    parser.add_argument('--barCodeNo', default='4119000000005')
    parser.add_argument('--sequenceNo', default='15033100004')
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
    url = request.route_url('famiport.api.reservation.customer')
    res = requests.post(url, params=params)
    print(res.content)

if __name__ == '__main__':
    main()
