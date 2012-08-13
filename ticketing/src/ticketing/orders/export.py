from ..carts.helpers import format_number as _format_number

def format_number(value):
    return _format_number(float(value))

class OrderCSV(object):
    order_value_filters = dict((k, format_number) for k in ['transaction_fee', 'delivery_fee', 'system_fee', 'total_amount'])

    # csv header
    order_header = [
        'order_no',
        'status',
        'created_at',
        'paid_at',
        'delivered_at',
        'canceled_at',
        'total_amount',
        'transaction_fee',
        'delivery_fee',
        'system_fee',
        ]
    user_profile_header = [
        'last_name',
        'first_name',
        'last_name_kana',
        'first_name_kana',
        'nick_name',
        'sex',
        ]
    shipping_address_header = [
        'last_name',
        'first_name',
        'last_name_kana',
        'first_name_kana',
        'zip',
        'country',
        'prefecture',
        'city',
        'address_1',
        'address_2',
        'tel_1',
        'tel_2',
        'fax',
        'email',
        ]
    other_header = [
        'payment',
        'delivery',
        'event',
        'venue',
        'start_on',
        ]
    product_header = [
        'name',
        'price',
        'quantity',
        'other',
        ]

    def __init__(self, orders):
        # shipping_addressのヘッダーにはuser_profileのカラムと区別する為にprefix(shipping_)をつける
        self.header = self.order_header \
                    + self.user_profile_header \
                    + ['shipping_' + sa for sa in self.shipping_address_header] \
                    + self.other_header
        self.rows = [self._convert_to_csv(order) for order in orders]

    def _convert_to_csv(self, order):
        order_dict = record_to_multidict(order)
        order_dict.add('created_at', str(order.created_at))
        order_dict.add('status', order.status)
        order_list = [(column, self.order_value_filters.get(column, no_filter)(order_dict.get(column))) for column in self.order_header]

        if order.user:
            user_profile_dict = record_to_multidict(order.user.user_profile)
            user_profile_list = [(column, user_profile_dict.get(column)) for column in self.user_profile_header]
        else:
            user_profile_list = []

        shipping_address_dict = record_to_multidict(order.shipping_address)
        shipping_address_list = [('shipping_' + column, shipping_address_dict.get(column)) for column in self.shipping_address_header]

        other_list = [
            ('payment', order.payment_delivery_pair.payment_method.name),
            ('delivery', order.payment_delivery_pair.delivery_method.name),
            ('event', order.ordered_products[0].product.event.title),
            ('venue', order.ordered_products[0].ordered_product_items[0].product_item.performance.venue.name),
            ('start_on', order.ordered_products[0].ordered_product_items[0].product_item.performance.start_on),
        ]

        product_list = []
        for i, ordered_product in enumerate(order.ordered_products):
            for column in self.product_header:
                if column != 'other':
                    column_name = 'product_%s_%s' % (column, i)
                    if not column_name in self.header:
                        self.header.append(column_name)
                    if column == 'name':
                        product_list.append((column_name, ordered_product.product.name))
                    if column == 'price':
                        product_list.append((column_name, format_number(ordered_product.price)))
                    if column == 'quantity':
                        product_list.append((column_name, ordered_product.quantity))
                else:
                    for ordered_product_item in ordered_product.ordered_product_items:
                        for key, value in ordered_product_item.attributes.items():
                            if value and key in ['t_shirts_size', 'publicity', 'mail_permission', 'cont', 'old_id_number']:
                                column_name = '%s_%s' % (key, i)
                                if not column_name in self.header:
                                    self.header.append(column_name)

                                # for bj89ers
                                if key == 'mail_permission':
                                    value = '' if value is None else value
                                elif key == 'cont':
                                    value = u'新規' if value == 'no' else u'継続'

                                product_list.append((column_name, value))

        # encoding
        row = dict(order_list + user_profile_list + shipping_address_list + other_list + product_list)
        for key, value in row.items():
            if value:
                if not isinstance(value, unicode):
                    value = unicode(value)
                value = value.encode('cp932')
            else:
                value = ''
            row[key] = value

        return row


