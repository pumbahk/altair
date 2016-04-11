#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import argparse
import pymysql


class fins(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

csv.register_dialect('fins', fins)


def main():
    # 日本語使えるところまでもっていけなかったので、ステータスが英語で出力される。
    # CSVを出力したあとに、置換してあげると優しい
    parser = argparse.ArgumentParser(description=u'申し込まれた抽選のエントリを、CSVで出力する')
    parser.add_argument('-n', "--lot", required=True, help=u'')
    print "LotsEntry Download!!"
    args = parser.parse_args()

    save_entries(args)


def save_entries(args):

    # develop
    #host = 'localhost'
    #db = 'ticketing'
    #user = 'ticketing'
    #password = 'ticketing'

    host = 'dbmain.standby.altr'
    db = 'ticketing'
    user = 'ticketstar_ro'
    password = 'ticketing'

    client = pymysql.connect(host=host, db=db, user=user, passwd=password)
    cur = client.cursor()
    cur.execute('SET NAMES sjis')

    wf = open(str(args.lot) + '.csv', 'w+b')
    writer = csv.writer(wf, dialect='fins')

    sql = get_sql().format(args.lot, args.lot)

    cur.execute(sql)
    datas = cur.fetchall()
    write_result(writer, datas)


def write_result(writer, datas):
    header = u"状態", u"申し込み番号", u"希望順序", u"申し込み日", u"席種", u"枚数", u"イベント", u"会場", u"公演", u"公演コード", u"公演日", u"商品", u"決済方法", u"引取方法", u"配送先姓", u"配送先名", u"配送先姓(カナ)", u"配送先名(カナ)", u"郵便番号", u"国", u"都道府県", u"市区町村", u"住所1", u"住所2", u"電話番号1", u"電話番号2", u"FAX", u"メールアドレス1", u"メールアドレス2", u"性別", u"誕生日", u"メモ", u"姓", u"名", u"姓(カナ)", u"名(カナ)", u"ニックネーム", u"プロフィールに設定されている性別", u"プロフィールに設定されている誕生日", u"販売チャネル", u"ブラウザID", u"会員種別名", u"会員グループ名", u"会員種別ID"
    header = map(lambda name: name.encode('sjis'), header)
    writer.writerow(header)

    for row in datas:
        writer.writerow(row)

def get_sql():
    sql = u"""\
SELECT
    CASE
        WHEN LotEntryWish.withdrawn_at IS NOT NULL THEN 'user_canceled'
        WHEN LotEntryWish.elected_at IS NOT NULL THEN 'elected'
        WHEN LotEntryWish.rejected_at IS NOT NULL THEN 'rejected'
        WHEN LotEntryWish.canceled_at IS NOT NULL THEN 'canceled'
        WHEN LotElectWork.lot_entry_no IS NOT NULL THEN 'elect_reserve'
        WHEN LotRejectWork.lot_entry_no IS NOT NULL THEN 'reject_reserve'
        WHEN LotEntry.closed_at IS NOT NULL THEN 'end'
        ELSE 'entried'
    END AS `status`,
    LotEntry.entry_no AS `entry_no`,
    LotEntryWish.wish_order + 1 AS `wish_order`,
    LotEntryWish.created_at AS `created_at`,
    -- NULL,
    p_sum.stock_names AS `stock_names`,
    p_sum.total_quantity AS `total_quantity`,
    Event.title AS `event`,
    Venue.name AS `venue`,
    Performance.name AS `performance`,
    Performance.code AS `code`,
    Performance.start_on AS `start_on`,
    p_sum.names AS `product_name`,
    PaymentMethod.name AS `payment_method`,
    DeliveryMethod.name AS `delivery_method`,
    ShippingAddress.last_name AS `last_name`,
    ShippingAddress.first_name AS `first_name`,
    ShippingAddress.last_name_kana AS `last_name_kana`,
    ShippingAddress.first_name_kana AS `first_name_kana`,
    ShippingAddress.zip AS `zip`,
    ShippingAddress.country AS `country`,
    ShippingAddress.prefecture AS `prefecture`,
    ShippingAddress.city AS `city`,
    ShippingAddress.address_1 AS `address_1`,
    ShippingAddress.address_2 AS `address_2`,
    ShippingAddress.tel_1 AS `tel_1`,
    ShippingAddress.tel_2 AS `tel_2`,
    ShippingAddress.fax AS `fax`,
    ShippingAddress.email_1 AS `email_1`,
    ShippingAddress.email_2 AS `email_2`,
    LotEntry.gender AS `sex`,
    LotEntry.birthday AS `birthday`,
    LotEntry.memo AS `memo`,
    UserProfile.last_name AS `profile_last_name`,
    UserProfile.first_name AS `profile_first_name`,
    UserProfile.last_name_kana AS `profile_last_name_kana`,
    UserProfile.first_name_kana AS `profile_first_name_kana`,
    UserProfile.nick_name AS `nickname`,
    UserProfile.sex AS `profile_sex`,
    UserProfile.birthday AS `profile_birthday`,
    LotEntry.channel AS `channel`,
    LotEntry.browserid AS `browserid`,
    Membership.name AS `membership_name`,
    MemberGroup.name AS `membergroup_name`,
    UserCredential.auth_identifier AS `auth_identifier`,
    LotEntryAttribute.name AS `attribute_name`,
    LotEntryAttribute.value AS `attribute_value`,
    NULL
FROM LotEntryWish
     JOIN LotEntry
     ON LotEntryWish.lot_entry_id = LotEntry.id AND LotEntry.deleted_at IS NULL
     JOIN Performance
     ON LotEntryWish.performance_id = Performance.id AND Performance.deleted_at IS NULL
     JOIN Venue
     ON Performance.id = Venue.performance_id AND Venue.deleted_at IS NULL
     JOIN Lot
     ON LotEntry.lot_id = Lot.id AND Lot.deleted_at IS NULL
     JOIN PaymentDeliveryMethodPair as PDMP
     ON LotEntry.payment_delivery_method_pair_id = PDMP.id AND PDMP.deleted_at IS NULL
     JOIN PaymentMethod
     ON PDMP.payment_method_id = PaymentMethod.id AND PaymentMethod.deleted_at IS NULL
     JOIN DeliveryMethod
     ON PDMP.delivery_method_id = DeliveryMethod.id  AND DeliveryMethod.deleted_at IS NULL
     JOIN Event
     ON Lot.event_id = Event.id AND Event.deleted_at IS NULL
     JOIN ShippingAddress
     ON LotEntry.shipping_address_id = ShippingAddress.id AND ShippingAddress.deleted_at IS NULL
     JOIN (
         SELECT
             LotEntryProduct.lot_wish_id,
             sum(LotEntryProduct.quantity) as total_quantity,
             group_concat(Product.name) as names,
             group_concat(StockType.name) as stock_names
         FROM LotEntryProduct
              JOIN LotEntryWish
              ON LotEntryProduct.lot_wish_id = LotEntryWish.id AND LotEntryWish.deleted_at IS NULL
              JOIN LotEntry
              ON LotEntryWish.lot_entry_id = LotEntry.id AND LotEntry.deleted_at IS NULL
              JOIN Product
              ON LotEntryProduct.product_id = Product.id AND Product.deleted_at IS NULL
              JOIN StockType
              ON Product.seat_stock_type_id = StockType.id AND StockType.deleted_at IS NULL
         WHERE LotEntry.lot_id = {}
         AND LotEntryProduct.deleted_at IS NULL
         GROUP BY LotEntryProduct.lot_wish_id
     ) p_sum
     ON p_sum.lot_wish_id = LotEntryWish.id
     LEFT JOIN User
     ON LotEntry.user_id = User.id AND User.deleted_at IS NULL
     LEFT JOIN UserProfile
     ON User.id = UserProfile.user_id AND UserProfile.deleted_at IS NULL
     LEFT JOIN LotElectWork
     ON LotElectWork.lot_id = Lot.id
     AND LotElectWork.lot_entry_no = LotEntry.entry_no
     AND LotElectWork.wish_order = LotEntryWish.wish_order
     LEFT JOIN LotRejectWork
     ON LotRejectWork.lot_id = Lot.id
     AND LotRejectWork.lot_entry_no = LotEntry.entry_no
     LEFT JOIN Membership
     ON LotEntry.membership_id=Membership.id AND Membership.deleted_at IS NULL
     LEFT JOIN MemberGroup
     ON LotEntry.membergroup_id=MemberGroup.id AND MemberGroup.deleted_at IS NULL
     LEFT JOIN UserCredential
     ON LotEntry.user_id=UserCredential.user_id AND LotEntry.membership_id=UserCredential.membership_id AND UserCredential.deleted_at IS NULL
     LEFT JOIN LotEntryAttribute
     ON LotEntryAttribute.lot_entry_id = LotEntry.id
WHERE Lot.id = {}
     AND LotEntryWish.deleted_at IS NULL
ORDER BY entry_no, wish_order, attribute_name

"""
    return sql

if __name__ == '__main__':
    main()
