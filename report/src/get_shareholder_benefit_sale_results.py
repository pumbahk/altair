# -*- coding: utf-8 -*-
# 該当チケット番号はTKT-6525(【イーグルス】2018年株主優待販売実績データ抽出)
# イーグルスの試合日を指定して株主優待販売実績データを抽出するスクリプト
# 予約単位、席単位で2ファイル出力される
# 以下は抽出条件
# 公演日期間→PERF_FROM と PERF_TOを設定してください
# 会員グループ名→株主優待
# 受付ステータス→受付済み、配送済み（キャンセル以外）

import csv
import re
import sys
import traceback
from datetime import datetime

import woothee

from pymysql import connect, cursors

current_year = datetime.now().strftime('%Y')
ORDER_CSV_NAME = '{}_order_jisseki.csv'.format(current_year)
SEAT_CSV_NAME = '{}_seat_jisseki.csv'.format(current_year)
EAGLES_ORG_ID = 24
PERF_FROM = '2018-04-03 00:00:00'
PERF_TO = '2018-10-06 23:59:59'

order_select = """
SELECT
    DISTINCT `Order`.id AS order_id,
    `Order`.order_no AS order_no,
    ( `Order`.special_fee + `Order`.transaction_fee + `Order`.system_fee + `Order`.delivery_fee ) AS fee,
    `Order`.total_amount AS total_amount,
    `Order`.channel AS order_channel,
    `Order`.membership_id AS order_member_id,
    PointGrantHistoryEntry.granted_amount AS pot_amount,
    PaymentMethod.name AS p_name,
    DeliveryMethod.name AS d_name,
    `Order`.created_at AS ordered_at,
    Event.id AS event_id,
    Event.title AS event_name,
    Performance.id AS perf_id,
    Performance.name AS perf_name,
    DATE_FORMAT( Performance.start_on, '%m' ) AS start_month,
    DATE(Performance.start_on) AS start_on,
    SalesSegmentGroup.name AS sales_segment_group_name,
    MemberGroup.name AS mg_name,
    UserCredential.auth_identifier AS cred_auth,
    UserCredential.authz_identifier AS cred_authz,
    Cart.user_agent AS user_agent,
    Cart.id AS cart_id,
    Cart.channel AS cart_channel,
    Cart.order_no AS cart_no,
    Cart.membership_id AS cart_member_id"""

seat_select = """
SELECT
    DISTINCT OrderedProductItemToken.id AS ordered_product_item_token_id,
    Seat.id AS seat_id,
    Seat.name AS seat_name,
    ProductItem.name AS prod_name,
    OrderedProductItem.price AS price,
    `Order`.id AS order_id,
    `Order`.order_no AS order_no,
    `Order`.channel AS order_channel,
    `Order`.membership_id AS order_member_id,
    Cart.id AS cart_id,
    Cart.channel AS cart_channel,
    Cart.order_no AS cart_no,
    Cart.membership_id AS cart_member_id"""

common_sql = """
FROM
    `Order`
INNER JOIN Cart ON
    Cart.order_id = `Order`.id
INNER JOIN Performance ON
    Performance.id = `Order`.performance_id
INNER JOIN Event ON
    Event.id = Performance.event_id
INNER JOIN MemberGroup ON
    MemberGroup.id = `Order`.membergroup_id
INNER JOIN OrderedProduct ON
    OrderedProduct.order_id = `Order`.id
INNER JOIN Product ON
    Product.id = OrderedProduct.product_id
INNER JOIN SalesSegment ON
    SalesSegment.id = Product.sales_segment_id
INNER JOIN SalesSegmentGroup ON
    SalesSegmentGroup.id = SalesSegment.sales_segment_group_id
INNER JOIN OrderedProductItem ON
    OrderedProductItem.ordered_product_id = OrderedProduct.id
INNER JOIN ProductItem ON
    ProductItem.id = OrderedProductItem.product_item_id
INNER JOIN OrderedProductItemToken ON
    OrderedProductItemToken.ordered_product_item_id = OrderedProductItem.id
LEFT JOIN Seat ON
    Seat.id = OrderedProductItemToken.seat_id
INNER JOIN PointGrantHistoryEntry ON
    PointGrantHistoryEntry.order_id = `Order`.id
INNER JOIN UserCredential ON
    UserCredential.user_id = `Order`.user_id
INNER JOIN PaymentDeliveryMethodPair ON
    PaymentDeliveryMethodPair.id = `Order`.payment_delivery_method_pair_id
INNER JOIN DeliveryMethod ON
    DeliveryMethod.id = PaymentDeliveryMethodPair.delivery_method_id
INNER JOIN PaymentMethod ON
    PaymentMethod.id = PaymentDeliveryMethodPair.payment_method_id
WHERE
    1
    AND `Order`.organization_id = {org_id}
    AND `Order`.deleted_at IS NULL
    AND `Order`.canceled_at IS NULL
    AND `Order`.refunded_at IS NULL
    AND Cart.deleted_at IS NULL
    AND SalesSegment.deleted_at IS NULL
    AND SalesSegmentGroup.deleted_at IS NULL
    AND Performance.deleted_at IS NULL
    AND Event.deleted_at IS NULL
    AND MemberGroup.deleted_at IS NULL
    AND OrderedProduct.deleted_at IS NULL
    AND OrderedProductItem.deleted_at IS NULL
    AND OrderedProductItemToken.deleted_at IS NULL
    AND PointGrantHistoryEntry.deleted_at IS NULL
    AND UserCredential.deleted_at IS NULL
    AND PaymentDeliveryMethodPair.deleted_at IS NULL
    AND DeliveryMethod.deleted_at IS NULL
    AND PaymentMethod.deleted_at IS NULL
    AND MemberGroup.name = '株主優待'
    AND Performance.start_on BETWEEN '{perf_from}' AND '{perf_to}'
ORDER BY
    Event.id ASC,
    Performance.id ASC,
    `Order`.id ASC;
"""

order_sql, seat_sql = [(sql + common_sql).format(
    org_id=EAGLES_ORG_ID,
    perf_from=PERF_FROM,
    perf_to=PERF_TO
) for sql in [order_select, seat_select]]

order_cols = [
    ('order_id', unicode, u'オーダーID'),
    ('order_no', unicode, u'予約番号'),
    ('fee', unicode, u'合計手数料'),
    ('total_amount', unicode, u'合計金額'),
    ('pot_amount', unicode, u'付与ポイント数'),
    ('p_name', unicode, u'決済方法'),
    ('d_name', unicode, u'引取方法'),
    ('ordered_at', unicode, u'予約日時'),
    ('event_id', unicode, u'イベントID'),
    ('event_name', unicode, u'イベント名'),
    ('perf_id', unicode, u'公演ID'),
    ('perf_name', unicode, u'公演名'),
    ('start_month', unicode, u'公演開始月'),
    ('start_on', unicode, u'公演開始日'),
    ('sales_segment_group_name', unicode, u'販売区分'),
    ('mg_name', unicode, u'会員グループ名'),
    ('cred_auth', unicode, u'会員種別ID'),
    ('cred_authz', unicode, u'会員番号'),
    ('ua_type', unicode, u'端末'),
    ('user_agent', unicode, u'ユーザーエージェント'),
    # これ以降はcsv生成後に削除してOKなカラム（デバッグ・データの整合性チェック甩）
    ('order_member_id', unicode, u'削除OK'),
    ('order_channel', unicode, u'削除OK'),
    ('cart_id', unicode, u'削除OK'),
    ('cart_channel', unicode, u'削除OK'),
    ('cart_no', unicode, u'削除OK'),
    ('cart_member_id', unicode, u'削除OK'),
    ('membership', unicode, u'削除OK'),
    ('channel', unicode, u'削除OK')
]

seat_cols = [
    ('seat_id', unicode, u'座席ID'),
    ('seat_name', unicode, u'座席名'),
    ('prod_name', unicode, u'商品明細名'),
    ('price', unicode, u'商品明細単価'),
    ('order_id', unicode, u'オーダーID'),
    ('order_no', unicode, u'予約番号'),
    # これ以降はcsv生成後に削除してOKなカラム（デバッグ・データの整合性チェック甩）
    ('order_member_id', unicode, u'削除OK'),
    ('order_channel', unicode, u'削除OK'),
    ('cart_id', unicode, u'削除OK'),
    ('cart_channel', unicode, u'削除OK'),
    ('cart_no', unicode, u'削除OK'),
    ('cart_member_id', unicode, u'削除OK'),
]


def main():
    # production, staging
    conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308,
                   charset='utf8', cursorclass=cursors.DictCursor)

    # local
    # conn = connect(host='localhost', user='root', passwd='', db='ticketing', port=3306,
    #                charset='utf8', cursorclass=cursors.DictCursor)

    try:
        # 座席ごとの販売実績
        f = open(SEAT_CSV_NAME, 'w')
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(map(encode_to_cp932, (t[2] for t in seat_cols)))

        cur = conn.cursor()
        cur.execute(seat_sql)
        for row in cur:
            assertions(row)

            try:
                writer.writerow(map(encode_to_cp932, (t[1](row[t[0]]) for t in seat_cols)))
            except TypeError as err:
                sys.stderr.write(repr(row))
                sys.stderr.write(str(err))
                t, v, tb = sys.exc_info()
                print(traceback.format_exception(t, v, tb))

        # 予約ごとの販売実績
        f = open(ORDER_CSV_NAME, 'w')
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerow(map(encode_to_cp932, (t[2] for t in order_cols)))

        cur = conn.cursor()
        cur.execute(order_sql)
        for row in cur:
            assertions(row)

            row['channel'] = row['order_channel']
            row['membership'] = row['order_member_id']
            if row['membership'] is None:
                row['membership'] = '0'

            # user agent
            row['ua_type'] = detect_ua_type(row['user_agent'])

            # perf_name
            row['perf_name'] = re.sub(r'.*vs ?(.*)', r'vs \1', row['perf_name'])

            try:
                writer.writerow(map(encode_to_cp932, (t[1](row[t[0]]) for t in order_cols)))
            except TypeError as err:
                sys.stderr.write(repr(row))
                sys.stderr.write(str(err))
                t, v, tb = sys.exc_info()
                print(traceback.format_exception(t, v, tb))

    finally:
        conn.close()


def assertions(row):
    # channel
    assert (row['cart_channel'] == row['order_channel'])

    # order_no
    assert (row['cart_no'] == row['order_no'])

    # membership
    assert (row['cart_member_id'] == row['order_member_id'])


def detect_ua_type(user_agent):
    try:
        ua = woothee.parse(user_agent)
    except UnicodeDecodeError:
        sys.stderr.write(repr(user_agent))
        return 'pc'

    if ua['category'] == 'smartphone':
        if ua['os'] == 'Android':
            if 'Mobile' not in user_agent:
                ret = 'atab'
            else:
                ret = 'asp'
        elif ua['os'] in ['iPhone']:
            ret = 'isp'
        elif ua['os'] in ['iPad', 'iPod']:
            ret = 'itab'
        else:
            ret = 'sp'
    elif ua['category'] == 'mobilephone':
        ret = 'fp'
    else:
        ret = 'pc'
    return ret


def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.replace('\r\n', '').encode('cp932')
    except UnicodeEncodeError:
        print 'cannot encode character %s to cp932' % data
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'


if __name__ == '__main__':
    main()
