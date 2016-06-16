import sys
from pymysql import connect, cursors

order_table_name = 'order201605'
order_seat_table_name = 'order_seat201605'

sql_ordered_product = """
    SELECT DISTINCT
        OrderedProduct.order_id,
        OrderedProductItem.id AS item_id,
        OrderedProductItemToken.serial AS item_serial,
        ProductItem.name AS item_name,
        OrderedProductItem.price AS item_price,
        IFNULL(Seat.name, '') AS seat_name
    FROM OrderedProduct
    JOIN OrderedProductItem ON OrderedProductItem.ordered_product_id = OrderedProduct.id
    JOIN OrderedProductItemToken ON OrderedProductItemToken.ordered_product_item_id = OrderedProductItem.id
    JOIN Product ON Product.id = OrderedProduct.product_id
    JOIN ProductItem ON ProductItem.id = OrderedProductItem.product_item_id
    LEFT JOIN Seat ON Seat.id = OrderedProductItemToken.seat_id AND Seat.deleted_at IS NULL
    WHERE 1
        AND OrderedProduct.deleted_at IS NULL
        AND OrderedProductItem.deleted_at IS NULL
        AND OrderedProductItemToken.deleted_at IS NULL
        AND Product.deleted_at IS NULL
        AND ProductItem.deleted_at IS NULL
        AND OrderedProductItemToken.valid = '1'
        AND OrderedProduct.order_id in (%s)
"""

cols = [
    ('order_id', int),
    ('item_id', int),
    ('item_serial', int),
    ('item_name', unicode),
    ('item_price', int),
    ('seat_name', unicode),
]

def main():
    ticketing_conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308, charset='utf8', cursorclass=cursors.DictCursor)
    report_conn = connect(host='127.0.0.1', user='report', passwd='report', db='report', port=3306, charset='utf8', cursorclass=cursors.DictCursor)
    try:
        ticketing_cur = ticketing_conn.cursor()
        report_cur = report_conn.cursor()
        report_cur.execute("select order_id from %s order by id asc" % order_table_name)
        orders = report_cur.fetchall()

        sql_insert_order_seat = u'INSERT INTO %s (order_id, item_id, item_serial, item_name, item_price, seat_name)' % order_seat_table_name \
                              + u' VALUES (%s, %s, %s, %s, %s, %s)'
        length = 10000 # number of target orders for OrderedProduct selection in each bulk insert due to the max limit of mysql
        for i in range(0, len(orders) / length + 1):
            order_ids = ', '.join([str(order['order_id']) for order in orders[i*length:(i+1)*length]])
            ticketing_cur.execute(sql_ordered_product % order_ids)
            seats = ticketing_cur.fetchall()
            param = []
            for row in seats:
                 param.append([int(row['order_id']), int(row['item_id']), int(row['item_serial']), unicode(row['item_name']), int(row['item_price']), unicode(row['seat_name'])])
            try:
                report_cur.executemany(sql_insert_order_seat, param)
            except:
                sys.stderr.write(repr(param) + "\n")
                raise

        report_conn.commit()
    finally:
        ticketing_conn.close()
        report_conn.close()

if __name__ == '__main__':
    main()
