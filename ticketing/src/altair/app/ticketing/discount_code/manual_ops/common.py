# -*- coding: utf-8 -*-
import hashlib
import sys
from datetime import datetime

import six


def select_environment():
    args = sys.argv
    environment = args[1] if len(args) == 2 else "local"

    return environment


def get_config():
    config = {
        'client_name': 'eaglesticket',
        'is_eternal': 1,
        'ticket_only': 1,
        'headers': {
            'Host': 'eagles.fanclub.rakuten.co.jp',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'Connection': 'close'
        }
    }

    return config


def get_next_year():
    return six.text_type(datetime.now().year + 1)


def create_token_for_member_check(open_id, client_name, salt):
    h = hashlib.sha224()
    h.update(open_id)
    h.update(client_name)
    h.update(salt)
    return six.text_type(h.hexdigest())


def create_token_by_first_coupon_code(first_coupon_cd, client_name, salt):
    h = hashlib.sha224()
    h.update(first_coupon_cd)
    h.update(client_name)
    h.update(salt)
    return six.text_type(h.hexdigest())


def select_proxies(environment):
    if environment == 'local':
        proxies = {
            'http': 'http://dev-proxy.db.rakuten.co.jp:9504',
            'https': 'https://dev-proxy.db.rakuten.co.jp:9504',
        }
    elif environment == 'stg':
        proxies = {
            'http': 'http://rdcproxy1-stg.1a.vpc.altr',
            'https': 'https://rdcproxy1-stg.1a.vpc.altr',
        }
    else:
        raise ValueError('Selected wrong envirionment: {}'.format(environment))

    return proxies
