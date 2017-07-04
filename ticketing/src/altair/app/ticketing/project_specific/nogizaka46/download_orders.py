# encoding: utf-8

import csv
from sqlalchemy.orm.session import make_transient

from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.orders.export import OrderDeltaCSV, get_japanese_columns
from altair.app.ticketing.orders.models import Order, OrderSummary

# 楽天チケットのORG_ID
ORG_ID = 15

# インポート用のカランのみ抽出
option_columns = [
    u'order.order_no',
    u'order.status',
    u'order.payment_status',
    u'order.created_at',
    u'order.paid_at',
    u'order.delivered_at',
    u'order.canceled_at',
    u'order.created_from_lot_entry.lot.name',
    u'order.total_amount',
    u'order.transaction_fee',
    u'order.delivery_fee',
    u'order.system_fee',
    u'order.special_fee',
    u'order.margin',
    u'order.refund_total_amount',
    u'order.refund_transaction_fee',
    u'order.refund_delivery_fee',
    u'order.refund_system_fee',
    u'order.refund_special_fee',
    u'order.note',
    u'order.special_fee_name',
    u'order.card_brand',
    u'order.card_ahead_com_code',
    u'order.card_ahead_com_name',
    u'order.issuing_start_at',
    u'order.issuing_end_at',
    u'order.payment_start_at',
    u'order.payment_due_at',
    u'sej_order.billing_number',
    u'sej_order.exchange_number',
    u'mail_magazine.mail_permission',
    u'user_profile.last_name',
    u'user_profile.first_name',
    u'user_profile.last_name_kana',
    u'user_profile.first_name_kana',
    u'user_profile.nick_name',
    u'user_profile.sex',
    u'membership.name',
    u'membergroup.name',
    u'user_credential.authz_identifier',
    u'shipping_address.last_name',
    u'shipping_address.first_name',
    u'shipping_address.last_name_kana',
    u'shipping_address.first_name_kana',
    u'shipping_address.zip',
    u'shipping_address.country',
    u'shipping_address.prefecture',
    u'shipping_address.city',
    u'shipping_address.address_1',
    u'shipping_address.address_2',
    u'shipping_address.tel_1',
    u'shipping_address.tel_2',
    u'shipping_address.fax',
    u'shipping_address.email_1',
    u'shipping_address.email_2',
    u'payment_method.name',
    u'delivery_method.name',
    u'event.title',
    u'performance.name',
    u'performance.code',
    u'performance.start_on',
    u'venue.name',
    u'ordered_product.price',
    u'ordered_product.quantity',
    u'ordered_product.refund_price',
    u'ordered_product.product.name',
    u'ordered_product.product.sales_segment.sales_segment_group.name',
    u'ordered_product_item.product_item.name',
    u'ordered_product_item.price',
    u'ordered_product_item.quantity',
    u'ordered_product_item.refund_price',
    u'ordered_product_item.print_histories',
    u'seat.name',
    u'stock_holder.name'
]


# helper
def encode_to_cp932(data):
    if not hasattr(data, "encode"):
        return str(data)
    try:
        return data.encode('cp932')
    except UnicodeEncodeError:
        print 'cannot encode character %s to cp932' % data
        if data is not None and len(data) > 1:
            return ''.join([encode_to_cp932(d) for d in data])
        else:
            return '?'

class OrderDownloader():
    def __init__(self, request):
        self.request = request
        self.session = get_db_session(self.request, name="slave")

    def download(self, performance_id):
        orders = self.session.query(OrderSummary).filter(OrderSummary.organization_id == ORG_ID, OrderSummary.deleted_at == None) \
                                                .filter(Performance.id == performance_id) \
                                                .filter(Order.performance_id == Performance.id, Order.deleted_at == None, Order.canceled_at == None)

        orders._request = self.request
        kwargs = {}
        kwargs['export_type'] = OrderDeltaCSV.EXPORT_TYPE_SEAT
        kwargs['excel_csv'] = True
        order_csv = OrderDeltaCSV(self.request,
                                  organization_id=ORG_ID,
                                  localized_columns=get_japanese_columns(self.request),
                                  session=self.session,
                                  option_columns=option_columns,
                                  **kwargs)

        def _orders(orders):
            prev_order = None
            for order in orders:
                if prev_order is not None:
                    make_transient(prev_order)
                prev_order = order
                yield order

        def writer_factory(f):
            writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
            def writerow(columns):
                writer.writerow([encode_to_cp932(column) for column in columns])
            return writerow

        output = order_csv(_orders(orders), writer_factory)

        with open('nogizaka46_orders.csv', 'w') as f:
            for line in output:
                f.writelines(line)