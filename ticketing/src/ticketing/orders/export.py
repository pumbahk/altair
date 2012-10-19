# -*- coding: utf-8 -*-
from ticketing.cart.helpers import format_number as _format_number
from ticketing.core.models import no_filter
from ticketing.models import record_to_multidict
from ticketing.users.models import MailSubscription, MailMagazine
from collections import defaultdict

def format_number(value):
    return _format_number(float(value))

def _create_mailsubscription_cache(organization_id):
    D = defaultdict(str)
    query = MailSubscription.query.filter(MailSubscription.segment_id==MailMagazine.id)
    if organization_id:
        query = query.filter(MailMagazine.organization_id==organization_id)
    for ms in query:
        D[ms.email] = "1"
    return D

class OrderCSV(object):
    order_value_filters = dict((k, format_number) for k in ['transaction_fee', 'delivery_fee', 'system_fee', 'total_amount'])

    EXPORT_TYPE_ORDER = 1
    EXPORT_TYPE_SEAT = 2

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
        'note',
        ]
    user_profile_header = [
        'last_name',
        'first_name',
        'last_name_kana',
        'first_name_kana',
        'nick_name',
        'sex',
        ]
    member_header = [
        'membership_name',
        'membergroup_name',
        'membership_id',
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
        'performance',
        'performance_code',
        'venue',
        'start_on',
        ]
    product_header = [
        'name',
        'price',
        'quantity',
        'sales_segment',
        ]
    product_item_header = [
        'name',
        'price',
        'quantity',
        'ticket_printed_by',
        ]
    seat_header = [
        'name',
        ]

    def __init__(self, orders, export_type=EXPORT_TYPE_ORDER, organization_id=None):
        export_type = int(export_type)
        self.organization_id = organization_id
        # shipping_addressのヘッダーにはuser_profileのカラムと区別する為にprefix(shipping_)をつける
        self.header = self.order_header \
                    + self.user_profile_header \
                    + self.member_header \
                    + ['shipping_' + sa for sa in self.shipping_address_header] \
                    + self.other_header
        self._mailsubscription_cache = None
        self.rows = []

        for order in orders:
            rows = self._convert_to_csv(order, export_type)
            if export_type == self.EXPORT_TYPE_ORDER:
                self.rows.append(rows)
            else:
                self.rows += rows

    @property
    def mailsubscription_cache(self):
        if self._mailsubscription_cache is None:
            if "mail_permission_0" not in self.header:
                self.header.append("mail_permission_0")
            self._mailsubscription_cache = _create_mailsubscription_cache(self.organization_id)
        return self._mailsubscription_cache

    def encode(self, row):
        for key, value in row.items():
            if value:
                if not isinstance(value, unicode):
                    value = unicode(value)
                value = value.encode('cp932')
            else:
                value = ''
            row[key] = value
        return row

    def _convert_to_csv(self, order, export_type):
        order_dict = record_to_multidict(order)
        order_dict.add('created_at', str(order.created_at))
        order_dict.add('status', order.status)
        order_list = [(column, self.order_value_filters.get(column, no_filter)(order_dict.get(column))) for column in self.order_header]

        user_profile_list = []
        if order.user and order.user.user_profile:
            user_profile_dict = record_to_multidict(order.user.user_profile)
            user_profile_list = [(column, user_profile_dict.get(column)) for column in self.user_profile_header]

        member_list = []
        if order.user and order.user.user_credential:
            uc = order.user.user_credential[0]
            member_list.append(('membership_name', uc.membership.name))
            member_list.append(('membership_id', uc.auth_identifier))
        if order.user and order.user.member:
            member_list.append(('membergroup_name', order.user.member.membergroup.name))

        shipping_address_list = []
        if order.shipping_address:
            shipping_address_dict = record_to_multidict(order.shipping_address)
            shipping_address_list = [('shipping_' + column, shipping_address_dict.get(column)) for column in self.shipping_address_header]

        performance = order.performance
        other_list = [
            ('payment', order.payment_delivery_pair.payment_method.name),
            ('delivery', order.payment_delivery_pair.delivery_method.name),
            ('event', performance.event.title),
            ('performance', performance.name),
            ('performance_code', performance.code),
            ('venue', performance.venue.name),
            ('start_on', performance.start_on),
        ]

        product_list = []
        product_item_list = []
        seat_list = []
        product_dict = {}
        for i, ordered_product in enumerate(order.ordered_products):
            buffer = []
            for column in self.product_header:
                if export_type == self.EXPORT_TYPE_ORDER:
                    column_name = 'product_%s_%s' % (column, i)
                else:
                    column_name = 'product_%s' % column
                if not column_name in self.header:
                    self.header.append(column_name)

                if column == 'name':
                    buffer.append((column_name, ordered_product.product.name))
                if column == 'price':
                    buffer.append((column_name, format_number(ordered_product.price)))
                if column == 'quantity':
                    buffer.append((column_name, ordered_product.quantity))
                if column == 'sales_segment':
                    buffer.append((column_name, ordered_product.product.sales_segment.name))
            if export_type == self.EXPORT_TYPE_ORDER:
                product_list += buffer
            else:
                product_dict[i] = {'product':buffer}

            for j, ordered_product_item in enumerate(ordered_product.ordered_product_items):
                buffer = []
                for column in self.product_item_header:
                    if export_type == self.EXPORT_TYPE_ORDER:
                        column_name = 'product_item_%s_%s' % (column, j)
                    else:
                        column_name = 'product_item_%s' % column
                    if not column_name in self.header:
                        self.header.append(column_name)

                    if column == 'name':
                        buffer.append((column_name, ordered_product_item.product_item.name))
                    if column == 'price':
                        buffer.append((column_name, format_number(ordered_product_item.price)))
                    if column == 'quantity':
                        quantity = ordered_product.quantity
                        if ordered_product_item.seats:
                            if export_type == self.EXPORT_TYPE_ORDER:
                                quantity = len(ordered_product_item.seats)
                            else:
                                quantity = 1
                        buffer.append((column_name, quantity))
                    if column == 'ticket_printed_by':
                        operator_name = ''
                        if ordered_product_item.issued_at:
                            operator_name = ', '.join(list(set([(ph.operator.name) for ph in ordered_product_item.print_histories if ph.operator])))
                        buffer.append((column_name, operator_name))

                # for bj89ers
                for key, value in ordered_product_item.attributes.items():
                    if value and key in ['t_shirts_size', 'publicity', 'mail_permission', 'cont', 'old_id_number']:
                        column_name = '%s_%s' % (key, j)
                        if not column_name in self.header:
                            self.header.append(column_name)
                        if key == 'mail_permission':
                            value = '' if value is None else value
                        elif key == 'cont':
                            value = u'新規' if value == 'no' else u'継続'
                        buffer.append((column_name, value))

                if export_type == self.EXPORT_TYPE_ORDER:
                    product_item_list += buffer
                else:
                    product_dict[i]['product_item'] = {j:buffer}

                buffer = []
                for column in self.seat_header:
                    if export_type == self.EXPORT_TYPE_ORDER:
                        column_name = 'seat_%s_%s' % (column, i)
                    else:
                        column_name = 'seat_%s' % column
                    if not column_name in self.header:
                        self.header.append(column_name)

                    if column == 'name':
                        if export_type == self.EXPORT_TYPE_ORDER:
                            seat_name = ''
                            if ordered_product_item.seats:
                                seat_name = ', '.join([(seat.name) for seat in ordered_product_item.seats if seat.name])
                            buffer.append((column_name, seat_name))
                        else:
                            if ordered_product_item.seats:
                                for seat in ordered_product_item.seats:
                                    buffer.append((column_name, seat.name))
                            else:
                                buffer.append((column_name, ''))
                if export_type == self.EXPORT_TYPE_ORDER:
                    seat_list += buffer
                else:
                    product_dict[i]['seat'] = {j:buffer}

        if export_type == self.EXPORT_TYPE_ORDER:
            row = dict(
                order_list
                + user_profile_list
                + member_list
                + shipping_address_list
                + other_list
                + product_list
                + product_item_list
                + seat_list
            )
            if "shipping_email" in row and not row.get("mail_permission_0"):
                row["mail_permission_0"] = self.mailsubscription_cache[row["shipping_email"]]
            return self.encode(row)
        else:
            rows = []
            for i, values in product_dict.iteritems():
                for j, seats in values['seat'].iteritems():
                    for seat in seats:
                        row = dict(
                            order_list
                            + user_profile_list
                            + member_list
                            + shipping_address_list
                            + other_list
                            + values['product']
                            + values['product_item'][j]
                            + [seat]
                        )
                        if "shipping_email" in row and not row.get("mail_permission_0"):
                            row["mail_permission_0"] = self.mailsubscription_cache[row["shipping_email"]]
                        rows.append(self.encode(row))
            return rows
