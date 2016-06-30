# -*- coding: utf-8 -*-
# イーグルスの試合日を指定して席主ごとに試合日までの販売したチケット数の推移を計算するスクリプト

import argparse
import pymysql.cursors
from datetime import datetime
from collections import OrderedDict


select_performance_sql = """
                        select p.id from Performance p inner join Event e on p.event_id = e.id 
                        where e.organization_id = 24 
                        and date(p.start_on) = %s 
                         """

select_orderedproduct_sql= """
                    select op.id, op.quantity, o.created_at
                    from `OrderedProduct` op
                    inner join `Order` o on o.id = op.order_id
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

            cursor.execute(select_orderedproduct_sql, stock_type['id'])
            ordered_products = cursor.fetchall()
            # ticket_count = len(ordered_products)

            date_count_dict = OrderedDict()

            for ordered_product in ordered_products:
            	order_date = ordered_product['created_at'].date()
            	if order_date not in date_count_dict.keys():
            		date_count_dict[order_date] = ordered_product['quantity']
            	else:
            		count = date_count_dict[order_date]
            		date_count_dict[order_date] = count + ordered_product['quantity']

            ticket_count_sum = 0
            for key, value in date_count_dict.items():
                ticket_count_sum = ticket_count_sum + value
                print key, value

            print 'sum: ', ticket_count_sum
            print
    finally:
    	connection.close()

    

if __name__ == "__main__":
	main()
