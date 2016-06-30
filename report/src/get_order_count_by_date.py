# -*- coding: utf-8 -*-
# イベントに対して日にちごとの予約数を計算するスクリプト

import argparse
import pymysql.cursors
from datetime import datetime
from collections import OrderedDict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('event_id')
    args = parser.parse_args()
    # performance_id = args.performance_id
    event_id = args.event_id

    # Connect to the database
    connection = pymysql.connect(host='dbmain.standby.altr', user='ticketing', passwd='ticketing', port=3308, db='ticketing', charset='utf8', \
                                 cursorclass=pymysql.cursors.DictCursor)
    date_count_dict = OrderedDict()
    order_count = 0
    try:
        cursor = connection.cursor()
        select_sql = "select e.title, p.id, p.name, p.start_on, o.created_at from `Order` o inner join Performance p on o.performance_id = p.id \
                      inner join Event e on p.event_id = e.id where e.id = %s and o.deleted_at is null and o.caneled_at is null order by o.created_at asc"

        cursor.execute(select_sql, (event_id, ))
        orders = cursor.fetchall()
        order_count = len(orders)

        print event_id, orders[0]['title'], orders[0]['start_on']

        for order in orders:
        	order_date = order['created_at'].date()
        	if order_date not in date_count_dict.keys():
        		date_count_dict[order_date] = 1
        	else:
        		count = date_count_dict[order_date]
        		date_count_dict[order_date] = count + 1
    finally:
    	connection.close()

    for key, value in date_count_dict.items():
    	print key, value
    print 'sum: ', order_count

if __name__ == "__main__":
	main()
