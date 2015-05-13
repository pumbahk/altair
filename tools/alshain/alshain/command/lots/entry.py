#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import sys
import argparse
import warnings
import multiprocessing
import lxml.etree
import requests
from requests.auth import HTTPBasicAuth
from pit import Pit


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-V', '--verbose', default=False, action='store_true')
    parser.add_argument('-c', '--count', default=1, type=int)

    args = parser.parse_args(argv)
    if not args.verbose:
        warnings.simplefilter('ignore')

    stg_basic_setting = Pit.get('stg_basic_setting',
                                {'require': {'username': '',
                                             'password': '',
                                             }})
    url = args.url
    username = stg_basic_setting['username']
    password = stg_basic_setting['password']

    children = [multiprocessing.Process(target=buy, args=(url, username, password)) for ii in range(args.count)]
    for child in children:
        child.start()
    for child in children:
        child.join()


def buy(url, username, password):
    entry_url = url
    confirm_url = url + '/confirm'
    auth = HTTPBasicAuth(username, password)
    res = requests.get(ENTRY_URL, auth=auth, verify=False)
    data = {
        'last_name': '',
        'performanceName-0': [{'start_on': '2015-07-15T15:00:00+00:00', 'name': u'hrwogiahroiea', 'open_on': None, 'venue': u' \u6771\u4eac\u30b9\u30ab\u30a4\u30c4\u30ea\u30fc\u30bf\u30a6\u30f3\u5168\u57df', 'id': 18822, 'label': u'2015\u5e747\u670816\u65e5(\u6728)0\u664200\u5206  \u6771\u4eac\u30b9\u30ab\u30a4\u30c4\u30ea\u30fc\u30bf\u30a6\u30f3\u5168\u57df'}],
        'performanceDate-0': 18822,
        'stockType-0': 15467,
        'product-id-0-0': 596871,
        'product-quantity-0-0': 1,
        'payment_delivery_method_pair_id': 32403,
        'last_name': 'テスト',
        'first_name': 'テスト',
        'last_name_kana': 'テスト',
        'first_name_kana': 'テスト',
        'email_1': 'dev@ticketstar.jp',
        'email_1_confirm': 'dev@ticketstar.jp',
        'tel_1': '070-1111-2222',
        'tel_2': '070-1111-2222',
        'zip': '1000003',
        'prefecture': '東京都',
        'city': '千代田区',
        'address_1': '一ツ橋',
        'address_2': '五反田HSビル9F',
        'birthday.year': '1980',
        'birthday.month': 1,
        'birthday.day': 1,
        'sex': 2,
        'memo': 'a',
        }
    res = requests.post(entry_url, auth=auth, verify=False, cookies=res.cookies, data=data)

    element = lxml.etree.HTML(res.content)
    token = element.xpath('//form/input[@name="token"][1]/@value')[0]
    data = {'token': token}
    res = requests.post(confirm_url, auth=auth, verify=False, cookies=res.cookies, data=data)
    element = lxml.etree.HTML(res.content)
    entry_no = element.xpath('//div[@class="confirmBoxText"][1]/text()')[0]
    print(entry_no)


if __name__ == '__main__':
    main()
