# -*- coding:utf-8 -*-
import sys
import re
from pymysql import connect, cursors
import woothee

sql_select_per_order = """
    SELECT
        Event.id AS event_id,
        Event.title AS event_name,
        Performance.id AS perf_id,
        Performance.name AS perf_name,
        DATE(Performance.start_on) AS start_on,
        Cart.id AS cart_id,
        `Order`.id AS order_id,
        Cart.channel AS cart_channel,
        `Order`.channel AS order_channel,
        Cart.order_no AS cart_no,
        `Order`.order_no AS order_no,
        Cart.browserid AS cart_xbi,
        `Order`.browserid AS order_xbi,
        Cart.created_at AS carted_at,
        `Order`.created_at AS ordered_at,
        Cart.user_agent,
        CASE
            WHEN `Order`.canceled_at IS NOT NULL THEN 'canceled'
            WHEN delivered_at IS NOT NULL THEN 'delivered'
            ELSE 'ordered'
        END AS order_status,
        CASE
            WHEN `Order`.refund_id IS NOT NULL AND `Order`.refunded_at IS NULL THEN 'refunding'
            WHEN refunded_at IS NOT NULL THEN 'refunded'
            WHEN paid_at IS NOT NULL THEN 'paid'
            ELSE 'unpaid'
        END AS payment_status,
        CASE
            WHEN `Order`.delivered_at IS NOT NULL THEN 'delivered'
            ELSE 'undelivered'
        END AS delivery_status,
        PaymentMethod.payment_plugin_id AS payment_method,
        DeliveryMethod.delivery_plugin_id AS delivery_method,
        `Order`.total_amount AS total,
        `Order`.system_fee + `Order`.special_fee + `Order`.delivery_fee + `Order`.transaction_fee AS fee,
        (SELECT SUM(OrderedProductItem.quantity)
            FROM OrderedProductItem JOIN OrderedProduct ON OrderedProduct.id = OrderedProductItem.ordered_product_id
            WHERE OrderedProductItem.deleted_at IS NULL AND OrderedProduct.deleted_at IS NULL AND OrderedProduct.order_id = `Order`.id
        ) AS qty,
        (SELECT SUM(amount)
            FROM PointGrantHistoryEntry
            WHERE PointGrantHistoryEntry.order_id = `Order`.id AND deleted_at IS NULL
        ) AS point,
        IF(`Order`.membergroup_id > 0, (
            SELECT MemberGroup.name
            FROM MemberGroup
            WHERE MemberGroup.id = `Order`.membergroup_id
        ), '') AS fc_type,
        IF(`Order`.user_id > 0, (
            SELECT UserCredential.auth_identifier
            FROM UserCredential
            WHERE UserCredential.user_id = `Order`.user_id AND UserCredential.deleted_at IS NULL
        ), '') AS fc_id
    FROM `Order`
    JOIN Cart ON Cart.order_id = `Order`.id
    JOIN Performance ON Performance.id = `Order`.performance_id
    JOIN Event ON Event.id = Performance.event_id
    JOIN PaymentDeliveryMethodPair ON PaymentDeliveryMethodPair.id = `Order`.payment_delivery_method_pair_id
    JOIN PaymentMethod ON PaymentMethod.id = PaymentDeliveryMethodPair.payment_method_id
    JOIN DeliveryMethod ON DeliveryMethod.id = PaymentDeliveryMethodPair.delivery_method_id
    WHERE 1
        AND `Order`.deleted_at IS NULL
        AND `Order`.canceled_at IS NULL
        AND `Order`.organization_id = 24
        AND Cart.deleted_at IS NULL
        AND Performance.deleted_at IS NULL
        AND Event.deleted_at IS NULL
        AND Event.id IN (6481, 6601, 6614, 6647, 6697, 6700, 6794, 6808, 6854, 6882, 6915, 7003, 7100, 7119, 7150, 7257, 7413, 7677, 7691)
        AND Performance.start_on between '2016-05-01' AND '2016-06-01'
"""

cols = [
    ('event_id', int),
    ('event_name', unicode),
    ('perf_id', int),
    ('perf_name', unicode),
    ('start_on', str),
    ('cart_id', int),
    ('order_id', int),
    ('channel', int),
    ('order_no', str),
    ('cart_xbi', str),
    ('order_xbi', str),
    ('carted_at', str),
    ('ordered_at', str),
    ('ua_type', str),
    ('order_status', str),
    ('payment_status', str),
    ('delivery_status', str),
    ('payment_method', int),
    ('delivery_method', int),
    ('fc_type', unicode),
    ('fc_id', unicode),
    ('total', int),
    ('fee', int),
    ('qty', int),
    ('point', int),
]

order_table_name = 'order201605'

def main():
    ticketing_conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308, charset='utf8', cursorclass=cursors.DictCursor)
    report_conn = connect(host='127.0.0.1', user='report', passwd='report', db='report', port=3306, charset='utf8', cursorclass=cursors.DictCursor)
    try:
        ticketing_cur = ticketing_conn.cursor()
        ticketing_cur.execute(sql_select_per_order)
        orders = ticketing_cur.fetchall()
        for row in orders:
            # channel
            assert(row['cart_channel'] == row['order_channel'])
            row['channel'] = row['order_channel']

            # order_no
            assert(row['cart_no'] == row['order_no'])

            # user agent
            row['ua_type'] = detect_ua_type(row['user_agent'])

            # perf_name
            row['perf_name'] = re.sub(r'.*vs ?(.*)', r'vs \1', row['perf_name'])

            # fc_type
            if row['fc_type'] is None:
                row['fc_type'] = ''

            # fc_id
            if row['fc_id'] is None:
                row['fc_id'] = ''

            # point
            if row['point'] is None:
                row['point'] = 0

            try:
                report_cur = report_conn.cursor()
                # TODO Can be improved with bulk insert as in select_item.py
                report_cur.execute(u'INSERT INTO %s SET ' % order_table_name + u', '.join(u'%s = %%s' % t[0] for t in cols), tuple(t[1](row[t[0]]) for t in cols))
            except:
                sys.stderr.write(repr(row) + "\n")
                raise

        report_conn.commit()
    finally:
        ticketing_conn.close()
        report_conn.close()

def detect_ua_type(user_agent):
    try:
        ua = woothee.parse(user_agent)
    except UnicodeDecodeError:
        sys.stderr.write(repr(user_agent) + "\n")
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

if __name__ == '__main__':
    main()
