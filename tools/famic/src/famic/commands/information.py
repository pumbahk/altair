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
    uri = FamiPortReserveAPIURL.INFORMATION.value
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    default_host_port = '{}:{}'.format(DEFAULT_HOST, DEFAULT_PORT)
    parser = argparse.ArgumentParser()
    parser.add_argument('host', default=default_host_port, nargs='?')
    parser.add_argument('--uketukeCode', default='')
    parser.add_argument('--kogtoSubCode', default='')
    parser.add_argument('--reserveNumber', default='4000000000001')
    parser.add_argument('--infoKubun', default='')
    parser.add_argument('--kogtoCode', default='')
    parser.add_argument('--koenCode', default='')
    parser.add_argument('--authCode', default='')
    parser.add_argument('--storeCode', default='000009')

    args = parser.parse_args(argv)

    params = dict(args._get_kwargs())
    host = args.host
    url = '{}://{}/{}'.format(DEFAULT_PROTOCOL, host, uri)
    res = requests.post(url, params=params)
    print(res.body)


if __name__ == '__main__':
    main()
