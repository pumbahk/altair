import sys
import csv
import re
from pymysql import connect, cursors
import woothee

### {{{ sql
sql = """
    SELECT
        Event.id AS event_id,
        Event.title AS event_name,
        Performance.id AS perf_id,
        Performance.name AS perf_name,
        DATE_FORMAT(Performance.start_on, '%m') AS start_month,
        DATE(Performance.start_on) AS start_on,
        `Order`.order_no AS order_no,
        (SELECT GROUP_CONCAT(DISTINCT StockType.name ORDER BY StockType.name) FROM OrderedProduct JOIN Product ON Product.id = OrderedProduct.product_id JOIN StockType ON StockType.id = Product.seat_stock_type_id WHERE OrderedProduct.order_id = `Order`.id AND OrderedProduct.deleted_at IS NULL AND `Order`.id IS NOT NULL) AS prod_name,
        (SELECT SUM(quantity * price) FROM OrderedProduct WHERE OrderedProduct.order_id = `Order`.id AND OrderedProduct.deleted_at IS NULL AND `Order`.id IS NOT NULL) AS price,
        (SELECT SUM(quantity) FROM OrderedProduct WHERE OrderedProduct.order_id = `Order`.id AND OrderedProduct.deleted_at IS NULL AND `Order`.id IS NOT NULL) AS qty,
        ((SELECT SUM(quantity * price) FROM OrderedProduct WHERE OrderedProduct.order_id = `Order`.id AND OrderedProduct.deleted_at IS NULL AND `Order`.id IS NOT NULL)*(SELECT SUM(quantity) FROM OrderedProduct WHERE OrderedProduct.order_id = `Order`.id AND OrderedProduct.deleted_at IS NULL AND `Order`.id IS NOT NULL)) as total,
        (`Order`.special_fee+`Order`.transaction_fee+`Order`.system_fee+`Order`.delivery_fee) as fee,
        `Order`.total_amount AS total_amount,
        Seat.name AS seat_name,
        PointGrantHistoryEntry.granted_amount AS pot_amount,
        DATE(`Order`.created_at) AS ordered_at,
        MemberGroup.name AS mg_name, 
        UserCredential.auth_identifier AS cred_auth, 
        `Order`.user_id AS user_id,
        UserCredential.authz_identifier AS cred_authz,
        Cart.user_agent AS user_agent,
        PaymentMethod.name AS p_name, 
        DeliveryMethod.name AS d_name,
        Cart.id AS cart_id,
        `Order`.id AS order_id,
        Cart.channel AS cart_channel,
        `Order`.channel AS order_channel,
        Cart.order_no AS cart_no,
        `Order`.order_no AS order_no,
        Cart.membership_id AS cart_member_id,
        `Order`.membership_id AS order_member_id
    FROM Cart
    INNER JOIN Performance ON Performance.id = Cart.performance_id
    INNER JOIN Event ON Event.id = Performance.event_id
    INNER JOIN `Order` ON `Order`.id = Cart.order_id AND `Order`.deleted_at IS NULL AND `Order`.canceled_at IS NULL AND `Order`.refunded_at IS NULL
    INNER JOIN MemberGroup ON MemberGroup.id = `Order`.membergroup_id 
    INNER JOIN OrderedProduct ON OrderedProduct.order_id = `Order`.id
    INNER JOIN OrderedProductItem ON OrderedProductItem.ordered_product_id = OrderedProduct.id
    INNER JOIN OrderedProductItemToken ON OrderedProductItemToken.ordered_product_item_id = OrderedProductItem.id
    LEFT JOIN Seat ON Seat.id = OrderedProductItemToken.seat_id
    INNER JOIN PointGrantHistoryEntry ON PointGrantHistoryEntry.order_id = `Order`.id
    INNER JOIN UserCredential ON UserCredential.user_id = `Order`.user_id
    INNER JOIN PaymentDeliveryMethodPair ON PaymentDeliveryMethodPair.id = `Order`.payment_delivery_method_pair_id
    INNER JOIN DeliveryMethod ON DeliveryMethod.id = PaymentDeliveryMethodPair.delivery_method_id
    INNER JOIN PaymentMethod ON PaymentMethod.id = PaymentDeliveryMethodPair.payment_method_id
    WHERE 1
        AND Cart.organization_id = 24
        AND Event.organization_id = 24
        AND Cart.deleted_at IS NULL
        AND Performance.deleted_at IS NULL
        AND Event.deleted_at IS NULL
        AND MemberGroup.deleted_at IS NULL
        AND OrderedProduct.deleted_at IS NULL
        AND OrderedProductItem.deleted_at IS NULL
        AND OrderedProductItemToken.deleted_at IS NULL
        AND Seat.deleted_at IS NULL
        AND PointGrantHistoryEntry.deleted_at IS NULL
        AND UserCredential.deleted_at IS NULL
        AND PaymentDeliveryMethodPair.deleted_at IS NULL
        AND DeliveryMethod.deleted_at IS NULL
        AND PaymentMethod.deleted_at IS NULL
        AND MemberGroup.id IN (300070,304989,304993)
        AND Performance.start_on BETWEEN '2017-04-04 00:00:00' AND '2017-10-10 23:59:00'
    Order by Event.id;
"""
cols = [
    ('event_id', int),
    ('event_name', unicode),
    ('perf_id', int),
    ('perf_name', unicode),
    ('start_month', str),
    ('start_on', str),
    ('order_no', str),
    ('prod_name', unicode),
    ('price', int),
    ('qty', int),
    ('total', int),
    ('fee', int),
    ('total_amount', int),
    ('seat_name', unicode),
    ('pot_amount', int),
    ('ordered_at', str),
    ('mg_name', unicode),
    ('cred_auth', str),
    ('user_id', int),
    ('cred_authz', str),
    ('user_agent', str),
    ('p_name', unicode),
    ('d_name', unicode),
    ('cart_id', int),
    ('order_id', int),
    ('cart_channel', int),
    ('order_channel', int),
    ('cart_no', str),
    ('order_no', str),
    ('cart_member_id', int),
    ('order_member_id', int),
    ('ua_type', str),
    ('membership', int),
    ('channel', int)
]
### }}}

def main():
    filename = u'2017_hanbai_jiseki.csv'
    f = open(filename, 'w')
    writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
    writer.writerow(map(unicode, (t[0] for t in cols)))

    conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308, charset='utf8', cursorclass=cursors.DictCursor)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        for row in cur:
            # channel
            assert(row['cart_channel'] == row['order_channel'])
            row['channel'] = row['order_channel']

            # order_no
            assert(row['cart_no'] == row['order_no'])

            # membership
            assert(row['cart_member_id'] == row['order_member_id'])
            row['membership'] = row['order_member_id']
            if row['membership'] is None:
                row['membership'] = '0'

            # user agent
            row['ua_type'] = detect_ua_type(row['user_agent'])

            # perf_name
            row['perf_name'] = re.sub(r'.*vs ?(.*)', r'vs \1', row['perf_name'])

            try:
                writer.writerow(map(encode_to_cp932, (t[1](row[t[0]]) for t in cols)))
            except TypeError:
                sys.stderr.write(repr(row))
    finally:
        conn.close()

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
