# encoding: utf-8
import csv
import six
from ..datainterchange.fileio import (
    Column,
    RecordUnmarshaller,
    CSVRecordMarshaller,
    ZeroPaddedNumericString,
    NumericString,
    Integer,
    Decimal,
    ZeroPaddedInteger,
    SJISString,
    DateTime,
    HHMMTime,
    HHMMDuration,
    Boolean,
    NotBefore
    )
from codecs import getencoder
from datetime import date

shop_master_schema = [
    Column('shop_code', ZeroPaddedNumericString(length=5)),                                                 # 店番
    Column('shop_code_updated', Integer(length=1)),                                                         # 店番変更フラグ
    Column('company_code', ZeroPaddedNumericString(length=4)),                                              # 会社コード
    Column('company_code_updated', Integer(length=1)),                                                      # 会社コード変更フラグ
    Column('company_name', SJISString(length=40)),                                                          # 会社名
    Column('company_name_updated', Integer(length=1)),                                                      # 会社名変更フラグ
    Column('district_code', ZeroPaddedNumericString(length=2, nullable=True)),                              # ディストリクトコード
    Column('district_code_updated', Integer(length=1)),                                                     # ディストリクトコード変更フラグ
    Column('district_name', SJISString(length=40)),                                                         # ディストリクト名
    Column('district_name_updated', Integer(length=1)),                                                     # ディストリクト名変更フラグ
    Column('district_valid_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),        # ディストリクト有効開始日
    Column('district_valid_from_updated', Integer(length=1)),                                               # ディストリクト有効開始日変更フラグ
    Column('branch_code', NumericString(length=3)),                                                         # 営業所コード
    Column('branch_code_updated', Integer(length=1)),                                                       # 営業所コード変更フラグ
    Column('branch_name', SJISString(length=40)),                                                           # 営業所名称
    Column('branch_name_updated', Integer(length=1)),                                                       # 営業所名称変更フラグ
    Column('branch_valid_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),          # 営業所有効開始日
    Column('branch_valid_from_updated', Integer(length=1)),                                                 # 営業所有効開始日変更フラグ
    Column('shop_name', SJISString(length=30)),                                                             # 店名
    Column('shop_name_updated', Integer(length=1)),                                                         # 店名変更フラグ
    Column('shop_name_kana', SJISString(length=60)),                                                        # 店名フリガナ
    Column('shop_name_kana_updated', Integer(length=1)),                                                    # 店名フリガナ変更フラグ
    Column('shop_tel', SJISString(length=12)),                                                              # 電話番号
    Column('shop_tel_updated', Integer(length=1)),                                                          # 電話番号変更フラグ
    Column('prefecture_code', Integer(length=2)),                                                           # 都道府県コード
    Column('prefecture_code_updated', Integer(length=1)),                                                   # 都道府県コード変更フラグ
    Column('prefecture_name', SJISString(length=20)),                                                       # 都道府県名称
    Column('prefecture_name_updated', Integer(length=1)),                                                   # 都道府県名称変更フラグ
    Column('shop_address', SJISString(length=80)),                                                          # 店舗住所
    Column('shop_address_updated', Integer(length=1)),                                                      # 店舗住所変更フラグ
    Column('shop_open_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),             # 絶対店舗開店日
    Column('shop_open_from_updated', Integer(length=1)),                                                    # 絶対店舗開店日変更フラグ
    Column('zip', SJISString(length=8)),                                                                    # 郵便番号 (ハイフンあり)
    Column('zip_updated', Integer(length=1)),                                                               # 郵便番号変更フラグ
    Column('business_run_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),          # 店舗運営開始日
    Column('business_run_from_updated', Integer(length=1)),                                                 # 店舗運営開始日変更フラグ
    Column('shop_open_at', NumericString(length=4, nullable=False)),                                        # 開店時刻
    Column('shop_open_at_updated', Integer(length=1)),                                                      # 開店時刻変更フラグ
    Column('shop_close_at', NumericString(length=4, nullable=False)),                                       # 閉店時刻
    Column('shop_close_at_updated', Integer(length=1)),                                                     # 閉店時刻変更フラグ
    Column('business_hours', HHMMDuration(nullable=True)),                                                  # 営業時間
    Column('business_hours_updated', Integer(length=1)),                                                    # 営業時間変更フラグ
    Column('opens_24hours', Integer(length=1)),                                                             # 24時間営業フラグ
    Column('opens_24hours_updated', Integer(length=1)),                                                     # 24時間営業フラグ変更フラグ
    Column('closest_station', SJISString(length=41)),                                                       # 最寄駅
    Column('closest_station_updated', Integer(length=1)),                                                   # 最寄駅変更フラグ
    Column('liquor_available', Integer(length=1)),                                                          # 酒免許有無
    Column('liquor_available_updated', Integer(length=1)),                                                  # 酒免許有無変更フラグ
    Column('cigarettes_available', Integer(length=1)),                                                      # 煙草免許有無
    Column('cigarettes_available_updated', Integer(length=1)),                                              # 煙草免許有無変更フラグ
    Column('business_run_until', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),         # 店舗運営終了日
    Column('business_run_until_updated', Integer(length=1)),                                                # 店舗運営終了日変更フラグ
    Column('shop_open_until', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),            # 絶対店舗閉鎖日
    Column('shop_open_until_updated', Integer(length=1)),                                                   # 絶対店舗閉鎖日変更フラグ
    Column('business_paused_at', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),         # 一時閉鎖日
    Column('business_paused_at_updated', Integer(length=1)),                                                # 一時閉鎖日変更フラグ
    Column('business_continued_at', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),      # 店舗再開店日
    Column('business_continued_at_updated', Integer(length=1)),                                             # 店舗再開店日変更フラグ
    Column('latitude', Decimal(precision=8, scale=6)),                                                      # 緯度
    Column('latitude_updated', Integer(length=1)),                                                          # 緯度変更フラグ
    Column('longitude', Decimal(precision=9, scale=6)),                                                     # 経度
    Column('longitude_updated', Integer(length=1)),                                                         # 経度変更フラグ
    Column('atm_available', Integer(length=1)),                                                             # ATM有無
    Column('atm_available_updated', Integer(length=1)),                                                     # ATM有無変更フラグ
    Column('mmk_available', Integer(length=1)),                                                             # MMK有無
    Column('mmk_available_updated', Integer(length=1)),                                                     # MMK有無変更フラグ
    Column('atm_available_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),         # ATMサービス開始日
    Column('atm_available_from_updated', Integer(length=1)),                                                # ATMサービス開始日変更フラグ
    Column('mmk_available_from', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),         # MMKサービス開始日
    Column('mmk_available_from_updated', Integer(length=1)),                                                # MMKサービス開始日変更フラグ
    Column('atm_available_until', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),        # ATMサービス終了日
    Column('atm_available_until_updated', Integer(length=1)),                                               # ATMサービス終了日変更フラグ
    Column('mmk_available_until', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),        # MMKサービス終了日
    Column('mmk_available_until_updated', Integer(length=1)),                                               # MMKサービス終了日変更フラグ
    Column('renewal_start_at', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),           # 改装開始日
    Column('renewal_start_at_updated', Integer(length=1)),                                                  # 改装開始日変更フラグ
    Column('renewal_end_at', DateTime(length=8, pytype=date, format=u'%Y%m%d', nullable=True, constraints=[NotBefore(date(1900, 1, 1))])),             # 改装終了日
    Column('renewal_end_at_updated', Integer(length=1)),                                                    # 改装終了日変更フラグ
    Column('record_updated', Integer(length=1)),                                                            # レコード変更有無
    Column('status', ZeroPaddedNumericString(length=2)),                                                    # 店舗運営ステータス
    Column('paused', Integer(length=1)),                                                                    # 一時閉鎖期間中フラグ
    Column('deleted', Integer(length=1)),                                                                   # 削除フラグ
    ]

def make_marshaller(f, encoding='CP932'):
    encoder = getencoder(encoding)
    marshaller = CSVRecordMarshaller(shop_master_schema)
    def out(rendered):
        f.write(encoder(rendered)[0])
    def _(row):
        return marshaller(row, out)
    return _

def make_unmarshaller(f, encoding='CP932', exc_handler=None):
    def _(f):
        for r in csv.reader(f):
            yield [six.text_type(c, encoding) for c in r]
    return RecordUnmarshaller(shop_master_schema, exc_handler=exc_handler)(_(f))
