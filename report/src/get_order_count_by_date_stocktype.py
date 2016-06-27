# -*- coding: utf-8 -*-
# イーグルスの試合日を指定して席主ごとに試合日までの予約数の推移を計算するスクリプト


import argparse
import pymysql.cursors
from datetime import datetime
from collections import OrderedDict


select_performance_sql = """
                        select p.id from Performance p inner join Event e on p.event_id = e.id 
                        where e.organization_id = 24 
                        and date(p.start_on) = %s 
                         """

select_order_sql= """
                    select e.title, p.id, p.name, p.start_on, o.created_at 
                    from `Order` o  
                    inner join Performance p on o.performance_id = p.id
                    inner join Event e on p.event_id = e.id
                    inner join OrderedProduct op on op.order_id = o.id
                    inner join Product pr on pr.id = op.product_id
                    inner join StockType st on st.id = pr.seat_stock_type_id
                    where  pr.seat_stock_type_id = %s 
                    and o.deleted_at is null 
                    and o.canceled_at is null 
                    order by o.created_at asc
                  """

select_stocktype_sql = """
                        select st.id, st.name from StockType st 
                        inner join Performance p on st.event_id = p.event_id 
                        where p.id in (%s) order by st.event_id asc
                       """

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('performance_date')
    args = parser.parse_args()
    performance_date = args.performance_date

    # Connect to the database
    connection = pymysql.connect(host='dbmain.standby.altr', user='ticketing', passwd='ticketing', port=3308, db='ticketing', charset='utf8', \
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        cursor = connection.cursor()

        cursor.execute(select_performance_sql, performance_date)
        performance_ids = cursor.fetchall()
        performance_list = [performance_id['id'] for performance_id in performance_ids]
        
        cursor.execute(select_stocktype_sql % ', '.join(map(str, performance_list)))
        stock_types = cursor.fetchall()

        for stock_type in stock_types:
            print stock_type['id'], stock_type['name'].encode('utf-8')

            cursor.execute(select_order_sql, stock_type['id'])
            orders = cursor.fetchall()

            date_count_dict = OrderedDict()

            for order in orders:
            	order_date = order['created_at'].date()
            	if order_date not in date_count_dict.keys():
            		date_count_dict[order_date] = 1
            	else:
            		count = date_count_dict[order_date]
            		date_count_dict[order_date] = count + 1

            order_count_sum = 0
            for key, value in date_count_dict.items():
                order_count_sum = order_count_sum + value
                print key, value

            print 'sum: ', order_count_sum
            print
    finally:
    	connection.close()

    

if __name__ == "__main__":
	main()
