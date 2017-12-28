# -*- coding: utf-8 -*-
import urllib

import common as c
import requests


def main():
    """
:see https://confluence.rakuten-it.com/confluence/display/PSFCP/Members+Check+API

成功時:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/member_check_api.py
http://eagles.fanclub.rakuten.co.jp/api/members-check?start_year=2018&open_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2FrNmPCzshCVbzC2SulpKTnGlWg%3D%3D&end_year=2018&client_name=eaglesticket&token=d421bc248784509ade0555099b48c5c4451c4c98b62a899460cd4734&ticket_only=1&is_eternal=1
200
{"status":"OK","timestamp":"2017-12-28 13:14:05","members":[{"fc_member_id":1222984,"fc_member_no":"************0653","course_id":10041,"course_name":"3-STAR","course_logo_url":"//eagles.fanclub.rakuten.co.jp/contents/pc/img/clubselect/clubimg_10041.png","course_color":"","year":2018,"ticket_only":1,"admission_date":"2017-12-26 13:50:29","rakuten_relation_date":"2017-12-26 13:50:33"}]}


失敗時1 必要情報が欠けているなど:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/member_check_api.py
http://eagles.fanclub.rakuten.co.jp/api/members-check?start_year=&open_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2FrNmPCzshCVbzC2SulpKTnGlWg%3D%3D&end_year=2018&client_name=eaglesticket&token=d421bc248784509ade0555099b48c5c4451c4c98b62a899460cd4734&ticket_only=1&is_eternal=1
200
{"status":"NG","timestamp":"2017-12-28 13:21:44","error_cd":"PARAMETER_ERROR","message":"開始年度は必須です。"}


失敗時2 会員になっていない:
/Users/ts-motoi.a.komatsu/altair/deploy/env/bin/python /Users/ts-motoi.a.komatsu/altair/ticketing/src/altair/app/ticketing/discount_code/test_script/member_check_api.py
http://eagles.fanclub.rakuten.co.jp/api/members-check?start_year=2018&open_id=https%3A%2F%2Fmyid.rakuten.co.jp%2Fopenid%2Fuser%2FrNmPCzshCVbzC2SulpKTnDlWg%3D%3D&end_year=2018&client_name=eaglesticket&token=3e01e0de7f8d25b645652bf2fb4fe4bff065a07f4c6838248f2b7d02&ticket_only=1&is_eternal=1
200
{"status":"OK","timestamp":"2017-12-28 13:23:56","members":[]}


    """
    environment = c.select_environment()
    config = c.get_config()

    url = "http://eagles.fanclub.rakuten.co.jp/api/members-check"

    # STG会員ID：stgticketusers+1@gmail.com
    # :see 楽天認証で使えるテストユーザー https://confluence.rakuten-it.com/confluence/pages/viewpage.action?pageId=683119383
    # https://eagles.fanclub.gl.rakuten.co.jp/dummyRLogin/dummyRLoginInit?sp_id=24にアクセスして、レスポンスにあるfc_member_noが
    # あっていることを確認すること
    open_id = "https://myid.rakuten.co.jp/openid/user/rNmPCzshCVbzC2SulpKTnGlWg=="

    # サンプルとして例示されていた会員のOpenID
    # :see Members Check API https://confluence.rakuten-it.com/confluence/display/PSFCP/Members+Check+API
    # open_id = "https://myid.rakuten.co.jp/openid/user/4PXZmaYTHZTzC2SulpKTnGlWg=="

    salt = 'fkaQ01kgLL@'  # PROD, STG共通

    token = c.create_token_for_member_check(open_id, config['client_name'], salt)

    next_year = c.get_next_year()

    params = {
        "open_id": open_id,
        "client_name": config['client_name'],
        "token": token,
        "start_year": next_year,
        "end_year": next_year,
        'ticket_only': config['ticket_only'],
        'is_eternal': config['is_eternal']
    }

    proxies = c.select_proxies(environment)
    response = requests.post(url=url, data=params, proxies=proxies, verify=False, headers=config['headers'])

    print(response.status_code)
    print(response.text)


if __name__ == "__main__":
    # execute only if run as a script
    main()
