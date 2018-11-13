# -*- coding: utf-8 -*-

import json
import common as c
import requests


def main():
    """
:see https://confluence.rakuten-it.com/confluence/display/PSFCP/Cancel+Used+Coupon+API
    """
    environment = c.select_environment()
    config = c.get_config()
    url = "http://eagles.fanclub.rakuten.co.jp/api/coupon/cancel/used"

    usage_type = '1010'

    salt = '60eAb@%Fa7e?'  # STG
    # salt = 'Be#dA#c410F%'  # PROD

    coupons = [
        {'coupon_cd': 'EQWM7RFA7AGT'},  # 必須
        {'coupon_cd': 'EEQT7CY7WP74'},  # 任意で増やしてください
        {'coupon_cd': 'EEQTW3X3Q9LN'},  # 任意で増やしてください
    ]

    # STG会員ID：stgticketusers+1@gmail.com
    # :see マイページにログインしてクーポンコードを確認 https://eagles.fanclub.rakuten.co.jp/mypage/login/ridLogin
    first_coupon_code = coupons[0]['coupon_cd']

    token = c.create_token_by_first_coupon_code(first_coupon_code, config['client_name'], salt)

    usage_coupons = {
        "usage_type": usage_type,
        "coupons": coupons,
    }

    usage_coupons_json_format = json.dumps(usage_coupons)

    post_data = {
        "client_name": config['client_name'],
        "token": token,
        "used_coupons": usage_coupons_json_format
    }

    proxies = c.select_proxies(environment)

    print(url)
    response = requests.post(url, data=post_data, proxies=proxies, verify=False, headers=config['headers'])

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    # execute only if run as a script
    main()
