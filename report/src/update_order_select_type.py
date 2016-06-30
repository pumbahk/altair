import sys
from pymysql import connect, cursors
import argparse

sql_order = """
    SELECT
        selector
    FROM order13949
    LEFT JOIN order_select13949 ON 1
        AND order_select13949.cart_xbi = order13949.cart_xbi
        AND ABS(UNIX_TIMESTAMP(carted_at) - UNIX_TIMESTAMP(recorded_at)) < 5
    WHERE 1
        AND order_id = %s
        AND channel IN (1, 2)
    ORDER BY ABS(UNIX_TIMESTAMP(carted_at) - UNIX_TIMESTAMP(recorded_at)) ASC
    LIMIT 1
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('order_id', metavar='order_id', type=int, nargs=1)
    args = parser.parse_args()
    order_id = args.order_id[0]

    conn = connect(host='localhost', user='root', passwd='pass', db='work', charset='utf8', cursorclass=cursors.DictCursor)
    conn2 = connect(host='localhost', user='root', passwd='pass', db='work', charset='utf8', cursorclass=cursors.DictCursor)
    try:
        cur = conn.cursor()
        cur.execute(sql_order, (order_id, ))
        for row in cur:
            if row['selector'] is None:
                sys.stderr.write(("order_id=%s not found." % order_id) + "\n")
                continue
            try:
                cur2 = conn2.cursor()
                cur2.execute(u'UPDATE order13949 SET select_type = %s WHERE order_id = %s', (row['selector'], order_id))
            except:
                sys.stderr.write(repr(row) + "\n")
                raise

        conn2.commit()
    finally:
        conn.close()
        conn2.close()

if __name__ == '__main__':
    main()
