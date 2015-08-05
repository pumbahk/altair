# encoding: utf-8

import unittest
import six
from decimal import Decimal

class ShopMasterTest(unittest.TestCase):
    maxDiff = 16384

    def setUp(self):
        from datetime import date, time, timedelta
        self.marshalled = u'00000,1,0000,1,北海道ファミリーマート,1,01,1,北海道,1,20150101,1,001,1,北海道,1,20150101,1,札幌北1条,1,サッポロキタイチジョウ,1,0112523938,1,1,1,北海道,1,札幌市中央区北1条東1丁目4-1,1,20150201,1,060-0031,1,20150130,1,0000,1,2359,1,2400,1,1,1,札幌,1,1,1,1,1,,0,,0,,0,,0,35,0,135,0,1,1,1,1,20150201,1,20150201,1,,1,,1,,1,,1,1,01,0,0'
        self.unmarshalled = {
            'shop_code': u'00000',                              # 店番
            'shop_code_updated': 1,                             # 店番変更フラグ
            'company_code': u'0000',                            # 会社コード
            'company_code_updated': 1,                          # 会社コード変更フラグ
            'company_name': u'北海道ファミリーマート',          # 会社名
            'company_name_updated': 1,                          # 会社名変更フラグ
            'district_code': u'01',                             # ディストリクトコード
            'district_code_updated': 1,                         # ディストリクトコード変更フラグ
            'district_name': u'北海道',                         # ディストリクト名
            'district_name_updated': 1,                         # ディストリクト名変更フラグ
            'district_valid_from': date(2015, 1, 1),            # ディストリクト有効開始日
            'district_valid_from_updated': 1,                   # ディストリクト有効開始日変更フラグ
            'branch_code': u'001',                              # 営業所コード
            'branch_code_updated': 1,                           # 営業所コード変更フラグ
            'branch_name': u'北海道',                           # 営業所名称
            'branch_name_updated': 1,                           # 営業所名称変更フラグ
            'branch_valid_from': date(2015, 1, 1),              # 営業所有効開始日
            'branch_valid_from_updated': 1,                     # 営業所有効開始日変更フラグ
            'shop_name': u'札幌北1条',                          # 店名
            'shop_name_updated': 1,                             # 店名変更フラグ
            'shop_name_kana': u'サッポロキタイチジョウ',        # 店名フリガナ
            'shop_name_kana_updated': 1,                        # 店名フリガナ変更フラグ
            'shop_tel': u'0112523938',                          # 電話番号
            'shop_tel_updated': 1,                              # 電話番号変更フラグ
            'prefecture_code': 1,                               # 都道府県コード
            'prefecture_code_updated': 1,                       # 都道府県コード変更フラグ
            'prefecture_name': u'北海道',                       # 都道府県名称
            'prefecture_name_updated': 1,                       # 都道府県名称変更フラグ
            'shop_address': u'札幌市中央区北1条東1丁目4-1',     # 店舗住所
            'shop_address_updated': 1,                          # 店舗住所変更フラグ
            'shop_open_from': date(2015, 2, 1),                 # 絶対店舗開店日
            'shop_open_from_updated': 1,                        # 絶対店舗開店日変更フラグ
            'zip': u'060-0031',                                 # 郵便番号 (ハイフンあり)
            'zip_updated': 1,                                   # 郵便番号変更フラグ
            'business_run_from': date(2015, 1, 30),             # 店舗運営開始日
            'business_run_from_updated': 1,                     # 店舗運営開始日変更フラグ
            'shop_open_at': u'0000',                            # 開店時刻
            'shop_open_at_updated': 1,                          # 開店時刻変更フラグ
            'shop_close_at': u'2359',                           # 閉店時刻
            'shop_close_at_updated': 1,                         # 閉店時刻変更フラグ
            'business_hours': timedelta(days=1),                # 営業時間
            'business_hours_updated': 1,                        # 営業時間変更フラグ
            'opens_24hours': 1,                                 # 24時間営業フラグ
            'opens_24hours_updated': 1,                         # 24時間営業フラグ変更フラグ
            'closest_station': u'札幌',                         # 最寄駅
            'closest_station_updated': 1,                       # 最寄駅変更フラグ
            'liquor_available': 1,                              # 酒免許有無
            'liquor_available_updated': 1,                      # 酒免許有無変更フラグ
            'cigarettes_available': 1,                          # 煙草免許有無
            'cigarettes_available_updated': 1,                  # 煙草免許有無変更フラグ
            'business_run_until': None,                         # 店舗運営終了日
            'business_run_until_updated': 0,                    # 店舗運営終了日変更フラグ
            'shop_open_until': None,                            # 絶対店舗閉鎖日
            'shop_open_until_updated': 0,                       # 絶対店舗閉鎖日変更フラグ
            'business_paused_at': None,                         # 一時閉鎖日
            'business_paused_at_updated': 0,                    # 一時閉鎖日変更フラグ
            'business_continued_at': None,                      # 店舗再開店日
            'business_continued_at_updated': 0,                 # 店舗再開店日変更フラグ
            'latitude': Decimal(35.),                           # 緯度
            'latitude_updated': 0,                              # 緯度変更フラグ
            'longitude': Decimal(135.),                         # 経度
            'longitude_updated': 0,                             # 経度変更フラグ
            'atm_available': 1,                                 # ATM有無
            'atm_available_updated': 1,                         # ATM有無変更フラグ
            'mmk_available': 1,                                 # MMK有無
            'mmk_available_updated': 1,                         # MMK有無変更フラグ
            'atm_available_from': date(2015, 2, 1),             # ATMサービス開始日
            'atm_available_from_updated': 1,                    # ATMサービス開始日変更フラグ
            'mmk_available_from': date(2015, 2, 1),             # MMKサービス開始日
            'mmk_available_from_updated': 1,                    # MMKサービス開始日変更フラグ
            'atm_available_until': None,                        # ATMサービス終了日
            'atm_available_until_updated': 1,                   # ATMサービス終了日変更フラグ
            'mmk_available_until': None,                        # MMKサービス終了日
            'mmk_available_until_updated': 1,                   # MMKサービス終了日変更フラグ
            'renewal_start_at': None,                           # 改装開始日
            'renewal_start_at_updated': 1,                      # 改装開始日変更フラグ
            'renewal_end_at': None,                             # 改装終了日
            'renewal_end_at_updated': 1,                        # 改装終了日変更フラグ
            'record_updated': 1,                                # レコード変更有無
            'status': u'01',                                    # 店舗運営ステータス (何が来るか謎)
            'paused': 0,                                        # 一時閉鎖期間中フラグ
            'deleted': 0,                                       # 削除フラグ
            }

    def test_marshal(self):
        from .shop_master import make_marshaller
        from io import BytesIO
        f = BytesIO()
        m = make_marshaller(f)
        m(self.unmarshalled)
        self.assertEqual(six.text_type(f.getvalue().rstrip(), 'CP932'), self.marshalled)

    def test_unmarshal(self):
        from datetime import date, time, timedelta
        from .shop_master import make_unmarshaller
        from io import BytesIO
        f = BytesIO()
        f.write(self.marshalled.encode('CP932'))
        f.seek(0)
        m = make_unmarshaller(f)
        self.assertEqual(m.next(), self.unmarshalled)

