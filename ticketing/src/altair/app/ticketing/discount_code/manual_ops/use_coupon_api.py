# -*- coding: utf-8 -*-

import json
import common as c
import requests


def main():
    """
:see https://confluence.rakuten-it.com/confluence/display/PSFCP/Use+Coupon+API

成功時:
http://eagles.fanclub.rakuten.co.jp/api/coupon/use
200
{"status":"OK","timestamp":"2017-12-28 16:07:59","usage_type":"1010","use_result":"1010","fc_member_id":"1222984","coupons":[{"coupon_cd":"EQWM7RFA7AGT","coupon_type":"1010","available_flg":"1","reason_cd":"1010"}]}


失敗時 利用済：
http://eagles.fanclub.rakuten.co.jp/api/coupon/use
200
{"status":"OK","timestamp":"2017-12-28 16:10:59","usage_type":"1010","use_result":"1020","fc_member_id":"1222984","coupons":[{"coupon_cd":"EQWM7RFA7AGT","coupon_type":"1010","available_flg":"0","reason_cd":"1030"}]}
    """
    environment = c.select_environment()
    config = c.get_config()
    url = "http://eagles.fanclub.rakuten.co.jp/api/coupon/use"

    usage_type = '1010'

    fc_member_id = '1222984'

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
        "fc_member_id": fc_member_id,
        "coupons": coupons,
    }

    usage_coupons_json_format = json.dumps(usage_coupons)

    post_data = {
        "client_name": config['client_name'],
        "token": token,
        "usage_coupons": usage_coupons_json_format
    }

    proxies = c.select_proxies(environment)

    print(url)
    response = requests.post(url, data=post_data, proxies=proxies, verify=False, headers=config['headers'])

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    # execute only if run as a script
    main()
