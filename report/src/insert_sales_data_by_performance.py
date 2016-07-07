import sys
from pymysql import connect, cursors


sql_select_sales_by_performance = """
  SELECT
    p.id perf_id,
    p.name perf_name,
    date(p.start_on) start_date,
    date(p.end_on) end_date,
    e.id event_id,
    e.title event_name,
    a.id account_id,
    a.name account_name,
    sum(o.total_amount) total_sales,
    count(o.id) order_count_sum,
    sum(o.transaction_fee) transaction_fee_sum,
    sum(o.delivery_fee) delivery_fee_sum,
    sum(o.system_fee) system_fee_sum,
    sum(o.special_fee) special_fee_sum
  FROM `Order` o
  INNER JOIN Performance p on o.performance_id = p.id
  INNER JOIN Event e on p.event_id = e.id
  INNER JOIN Account a on a.id = coalesce(p.account_id, e.account_id) # join with Performance if p.account_id is not null else with Event
  WHERE 1
  AND   e.deleted_at is null
  AND   p.deleted_at is null
  AND   o.organization_id = 15
  AND   year(o.created_at) = 2016
  AND   o.deleted_at is null
  AND   o.canceled_at is null
  AND   o.refunded_at is null
  GROUP BY p.id
  HAVING order_count_sum > 0
  ORDER BY start_date
"""

sql_select_ticket_count_by_performance = """
  SELECT o.performance_id perf_id, sum(op.quantity) ticket_count_sum
  FROM OrderedProduct op
  INNER JOIN `Order` o on op.order_id = o.id
  WHERE 1
  AND   o.performance_id in (%s)
  AND   year(o.created_at) = 2016
  AND   o.deleted_at is null
  AND   o.canceled_at is null
  AND   o.refunded_at is null
  GROUP BY o.performance_id
"""

sql_select_order_count_by_payment_method = """
  SELECT
    o.performance_id perf_id,
    count(o.id) order_count_sum,
    sum(o.transaction_fee) transaction_fee_sum
  FROM `Order` o
  INNER JOIN PaymentDeliveryMethodPair pdmp on o.payment_delivery_method_pair_id = pdmp.id
  INNER JOIN PaymentMethod pm on pdmp.payment_method_id = pm.id
  WHERE 1
  AND   o.organization_id = 15
  AND   year(o.created_at) = 2016
  AND   o.deleted_at is null
  AND   o.canceled_at is null
  AND   o.refunded_at is null
  AND   pm.payment_plugin_id = %s
  GROUP BY perf_id
  HAVING order_count_sum > 0;
"""


sql_select_order_count_by_delivery_method = """
  SELECT
    o.performance_id perf_id,
    count(o.id) order_count_sum,
    sum(o.delivery_fee) delivery_fee_sum
  FROM `Order` o
  INNER JOIN PaymentDeliveryMethodPair pdmp on o.payment_delivery_method_pair_id = pdmp.id
  INNER JOIN DeliveryMethod dm on pdmp.delivery_method_id = dm.id
  WHERE 1
  AND   o.organization_id = 15
  AND   year(o.created_at) = 2016
  AND   o.deleted_at is null
  AND   o.canceled_at is null
  AND   o.refunded_at is null
  AND   dm.delivery_plugin_id = %s
  GROUP BY perf_id
  HAVING order_count_sum > 0;
"""

rt_sales_table_name = 'rt_sales2016'

def main():
    ticketing_conn = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308, charset='utf8', cursorclass=cursors.DictCursor)
    report_conn = connect(host='127.0.0.1', user='report', passwd='report', db='report', port=3306, charset='utf8', cursorclass=cursors.DictCursor)
    try:
        ticketing_cur = ticketing_conn.cursor()
        report_cur = report_conn.cursor()

        # Insert sales data by performance
        ticketing_cur.execute(sql_select_sales_by_performance)
        performances = ticketing_cur.fetchall()

        sql_insert_order_seat = u'INSERT INTO %s (perf_id, perf_name, start_date, end_date, account_name, event_id, event_name, total_sales, order_count_sum, transaction_fee_sum, \
                                delivery_fee_sum, system_fee_sum, special_fee_sum)' % rt_sales_table_name + u' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        param = []
        perf_id_list = []
        for row in performances:
            param.append([int(row['perf_id']), unicode(row['perf_name']), str(row['start_date']), str(row['end_date']) if row['end_date'] else None, unicode(row['account_name']),
                          int(row['event_id']), unicode(row['event_name']), int(row['total_sales']), int(row['order_count_sum']), int(row['transaction_fee_sum']),
                          int(row['delivery_fee_sum']), int(row['system_fee_sum']), int(row['special_fee_sum'])])
            perf_id_list.append(str(row['perf_id']))

        try:
            report_cur.executemany(sql_insert_order_seat, param)
        except:
            sys.stderr.write(repr(param) + "\n")
            raise

        report_conn.commit()

        # Set ticket_count_sum
        ticketing_cur.execute(sql_select_ticket_count_by_performance % ', '.join(perf_id_list))
        results = ticketing_cur.fetchall()
        sql_update_ticket_count_sum = 'UPDATE ' + rt_sales_table_name + ' SET ticket_count_sum = %s WHERE perf_id = %s'
        report_conn.begin()
        for result in results:
            try:
                report_cur.execute(sql_update_ticket_count_sum % (str(result['ticket_count_sum']), str(result['perf_id'])))
            except:
                sys.stderr.write('perf_id: %s, ticket_count_sum: %s' % (str(result['perf_id']), str(result['ticket_count_sum'])) + "\n")
                raise
        report_conn.commit()

        # Set order_count_sum and transaction_fee_sum by payment method
        payment_plugin_list = {('order_count_creditcard', 'transaction_fee_creditcard', 1), ('order_count_rakuten_payment', 'transaction_fee_rakuten', 2), \
                               ('order_count_sej_payment', 'transaction_fee_sej', 3), ('order_count_reserve_payment', 'transaction_fee_reserve', 4), \
                               ('order_count_famiport_payment', 'transaction_fee_famiport', 6)} # Free payment is excluded
        report_conn.begin()
        for order_count_column, transaction_fee_column, payment_plugin_id in payment_plugin_list:
            sql_update_sales_data_by_payment_method = 'UPDATE ' + rt_sales_table_name + ' SET ' + order_count_column + ' = %s, ' + transaction_fee_column + ' = %s WHERE perf_id = %s'
            ticketing_cur.execute(sql_select_order_count_by_payment_method % str(payment_plugin_id))
            results_by_payment_method = ticketing_cur.fetchall()
            for result_by_payment_method in results_by_payment_method:
                try:
                    report_cur.execute(sql_update_sales_data_by_payment_method %
                                      (str(result_by_payment_method['order_count_sum']), str(result_by_payment_method['transaction_fee_sum']), str(result_by_payment_method['perf_id']))
                                      )
                except:
                    sys.stderr.write('perf_id: %s, order_count_sum: %s, transaction_fee_sum: %s' %
                                    (str(result_by_payment_method['perf_id']), str(result_by_payment_method['order_count_sum']), str(result_by_payment_method['transaction_fee_sum'])) + "\n")
                    raise
            report_conn.commit()

        # Set order_count_sum and delivery_fee_sum by delivery method
        delivery_plugin_list = {('order_count_shipping_delivery', 'delivery_fee_shipping', 1), ('order_count_sej_delivery', 'delivery_fee_sej', 2), \
                               ('order_count_reserve_delivery', 'delivery_fee_reserve', 3), ('order_count_qr_delivery', 'delivery_fee_qr', 4), \
                               ('order_count_orion_delivery', 'delivery_fee_orion', 5), ('order_count_famiport_delivery', 'delivery_fee_famiport', 6)}
        report_conn.begin()
        for order_count_column, delivery_fee_column, delivery_plugin_id in delivery_plugin_list:
            sql_update_sales_data_by_delivery_method = 'UPDATE ' + rt_sales_table_name + ' SET ' + order_count_column + ' = %s, ' + delivery_fee_column + ' = %s WHERE perf_id = %s'
            ticketing_cur.execute(sql_select_order_count_by_delivery_method % str(delivery_plugin_id))
            results_by_delivery_method = ticketing_cur.fetchall()
            for result_by_delivery_method in results_by_delivery_method:
                try:
                    report_cur.execute(sql_update_sales_data_by_delivery_method %
                                      (str(result_by_delivery_method['order_count_sum']), str(result_by_delivery_method['delivery_fee_sum']), str(result_by_delivery_method['perf_id']))
                                      )
                except:
                    sys.stderr.write('perf_id: %s, order_count_sum: %s, delivery_fee_sum: %s' %
                                    (str(result_by_delivery_method['perf_id']), str(result_by_delivery_method['order_count_sum']), str(result_by_delivery_method['delivery_fee_sum'])) + "\n")
                    raise
            report_conn.commit()

    finally:
        ticketing_conn.close()
        report_conn.close()


if __name__ == '__main__':
    main()
