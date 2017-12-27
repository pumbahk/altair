# -*- coding: utf-8 -*-
import json
import common as c
import requests


def main():
    """
:see https://confluence.rakuten-it.com/confluence/display/PSFCP/Confirm+Coupon+Status+API

成功時1 正常系:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/confirm_coupon_status_api.py
200
{"status":"OK","timestamp":"2017-12-28 13:24:57","usage_type":"1010","fc_member_id":"1222984","coupons":[{"coupon_cd":"EQWM7RFA7AGT","coupon_type":"1010","name":"テストクーポン0000","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EEQT7CY7WP74","coupon_type":"1010","name":"2018年入会特典　1試合チケット引換券","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EEQTW3X3Q9LN","coupon_type":"1010","name":"2018年入会特典　1試合チケット引換券","available_flg":"1","reason_cd":"1010"}]}


成功時2 有効なコードの重複入力（available_flのgが１で返って来るので注意）:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/confirm_coupon_status_api.py
200
{"status":"OK","timestamp":"2017-12-28 13:24:57","usage_type":"1010","fc_member_id":"1222984","coupons":[{"coupon_cd":"EQWM7RFA7AGT","coupon_type":"1010","name":"テストクーポン0000","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EEQT7CY7WP74","coupon_type":"1010","name":"2018年入会特典　1試合チケット引換券","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EEQTW3X3Q9LN","coupon_type":"1010","name":"2018年入会特典　1試合チケット引換券","available_flg":"1","reason_cd":"1010"}]}


失敗時1 必要情報が欠けているなど:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/confirm_coupon_status_api.py
200
{"status":"NG","timestamp":"2017-12-28 13:25:39","error_cd":"AUTH_ERROR","message":"トークンの認証に失敗しました。"}


失敗時2 記号が混ざっている:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/confirm_coupon_status_api.py
200
{"status":"NG","timestamp":"2017-12-28 13:26:28","error_cd":"PARAMETER_ERROR","message":"3番目のクーポンコードが半角英数字 12桁ではありません。"}


失敗時3 存在しないクーポンコード（３つめのコードがそれ）:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/confirm_coupon_status_api.py
200
{"status":"OK","timestamp":"2017-12-28 13:27:05","usage_type":"1010","fc_member_id":"1222984","coupons":[{"coupon_cd":"EQWM7RFA7AGT","coupon_type":"1010","name":"テストクーポン0000","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EEQT7CY7WP74","coupon_type":"1010","name":"2018年入会特典　1試合チケット引換券","available_flg":"1","reason_cd":"1010"},{"coupon_cd":"EESEOIJE4IJO","coupon_type":"","name":"","available_flg":"0","reason_cd":"2010"}]}


    """
    environment = c.select_environment()
    config = c.get_config()

    url = "http://eagles.fanclub.rakuten.co.jp/api/coupon/confirm/status"

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

    confirmation_condition = {
        "usage_type": usage_type,
        "fc_member_id": fc_member_id,
        "coupons": coupons,
    }

    confirmation_condition_json_format = json.dumps(confirmation_condition)

    post_data = {
        "client_name": config['client_name'],
        "token": token,
        "confirmation_condition": confirmation_condition_json_format
    }

    proxies = c.select_proxies(environment)

    print(url)
    response = requests.post(url, data=post_data, proxies=proxies, verify=False,
                             headers=config['headers'])

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    # execute only if run as a script
    main()
