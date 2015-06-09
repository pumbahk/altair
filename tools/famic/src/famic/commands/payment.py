# -*- coding: utf-8 -*-
import sys
import datetime
import argparse
import requests
from famic.utils import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    FamiPortReserveAPIURL,
    )
from famic.crypto import KusoCrypto


def main(argv=sys.argv[1:]):
    uri = FamiPortReserveAPIURL.PAYMENT.value
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    default_host_port = '{}:{}'.format(DEFAULT_HOST, DEFAULT_PORT)
    parser = argparse.ArgumentParser()
    parser.add_argument('host', default=default_host_port, nargs='?')
    parser.add_argument('--ticketingDate', default=now_str)
    parser.add_argument('--playGuideId', default='')
    parser.add_argument('--phoneNumber', default='rfanmRgUZFRRephCwOsgbg%3d%3d')
    parser.add_argument('--customerName', default='pT6fj7ULQklIfOWBKGyQ6g%3d%3d')
    parser.add_argument('--mmkNo', default='01')
    parser.add_argument('--barCodeNo', default='1000000000000')
    parser.add_argument('--sequenceNo', default='15033100002')
    parser.add_argument('--storeCode', default='000009')
    args = parser.parse_args(argv)

    params = dict(args._get_kwargs())

    crypto = KusoCrypto(params['barCodeNo'])
    params['customerName'] = crypto.encrypt(params['customerName'])
    params['phoneNumber'] = crypto.encrypt(params['phoneNumber'])

    host = args.host
    url = '{}://{}/{}'.format(DEFAULT_PROTOCOL, host, uri)
    res = requests.post(url, params=params)
    print(res.content)

if __name__ == '__main__':
    main()
