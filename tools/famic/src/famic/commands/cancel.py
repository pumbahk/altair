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


def main(argv=sys.argv[1:]):
    uri = FamiPortReserveAPIURL.CANCEL.value
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    default_host_port = '{}:{}'.format(DEFAULT_HOST, DEFAULT_PORT)
    parser = argparse.ArgumentParser()
    parser.add_argument('host', default=default_host_port, nargs='?')
    parser.add_argument('--storeCode', default='000009')
    parser.add_argument('--mmkNo', default='01')
    parser.add_argument('--sequenceNo', default='15033100002')
    parser.add_argument('--barCodeNo', default='1000000000000')
    parser.add_argument('--ticketingDate', default=now_str)
    parser.add_argument('--playGuideId', default='')
    parser.add_argument('--orderId', default='')
    parser.add_argument('--cancelCode', default='')

    args = parser.parse_args(argv)

    params = dict(args._get_kwargs())
    host = args.host
    url = '{}://{}/{}'.format(DEFAULT_PROTOCOL, host, uri)
    res = requests.post(url, params=params)
    print(res.content)

if __name__ == '__main__':
    main()
