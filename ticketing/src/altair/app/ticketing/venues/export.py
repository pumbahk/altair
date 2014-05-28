# -*- coding: utf-8 -*-

from collections import OrderedDict

from altair.app.ticketing.models import record_to_multidict
from altair.app.ticketing.core.models import SeatStatusEnum

def encode_to_cp932(row):
    encoded = {}
    for key, value in row.items():
        if value:
            if not isinstance(value, unicode):
                value = unicode(value)
            value = value.encode('cp932')
        else:
            value = ''
        encoded[key.encode('cp932')] = value
    return encoded

class SeatCSV(object):

    # csv header
    seat_header = OrderedDict([
        ('id', u'座席ID'),
        ('l0_id', u'l0_id'),
        ('seat_no', u'座席番号'),
        ('name', u'座席名'),
    ])
    stock_attribute_header = OrderedDict([
        ('floor', u'フロア'),
        ('gate', u'ゲート'),
        ('row', u'列番号'),
    ])
    stock_type_header = OrderedDict([
        ('id', u'席種ID'),
        ('name', u'席種名'),
    ])
    stock_holder_header = OrderedDict([
        ('id', u'枠ID'),
        ('name', u'枠名'),
    ])
    account_header = OrderedDict([
        ('id', u'配券先ID'),
        ('name', u'配券先名'),
    ])
    seat_status_header = OrderedDict([
        ('status', u'座席ステータス'),
        ('order_no', u'予約番号'),
    ])

    excluded_order_statuses = ['canceled']

    def __init__(self, seat_order_pairs):
        self.header = self.seat_header.values()\
                    + self.stock_attribute_header.values()\
                    + self.stock_type_header.values()\
                    + self.stock_holder_header.values()\
                    + self.account_header.values()\
                    + self.seat_status_header.values()
        self.header = [column.encode('cp932') for column in self.header]
        self.seat_order_pairs = seat_order_pairs
        self.seat_rendered = set()

    def _convert_to_csv(self, seat_order_pair):
        seat, order = seat_order_pair

        valid_order = order and order.status not in self.excluded_order_statuses
        if (not valid_order) and (seat.id in self.seat_rendered):
            return None

        row_data = []
        def get_row_data(header, data):
            data = record_to_multidict(data)
            return [(label, data.get(column)) for column, label in header.items()]

        def add_row_data(header, data):
            row_data.extend(get_row_data(header, data))

        add_row_data(self.seat_header, seat)
        if seat.stock.stock_type:
            add_row_data(self.stock_type_header, seat.stock.stock_type)
        if seat.stock.stock_holder:
            add_row_data(self.stock_holder_header, seat.stock.stock_holder)
            if seat.stock.stock_holder.account:
                add_row_data(self.account_header, seat.stock.stock_holder.account)

        for k, v in seat.attributes.items():
            if k in self.stock_attribute_header:
                label = self.stock_attribute_header.get(k)
                row_data.append((label, v))

        for status in SeatStatusEnum:
            if status.v == seat.status:
                label = self.seat_status_header.get('status')
                row_data.append((label, status.k))
                break

        if valid_order:
            label = self.seat_status_header.get('order_no')
            row_data.append((label, order.order_no))

        self.seat_rendered.add(seat.id)

        # encoding
        row = dict(row_data)
        return encode_to_cp932(row)

    @property
    def rows(self):
        for seat_order_pair in self.seat_order_pairs:
            retval = self._convert_to_csv(seat_order_pair)
            if retval is not None:
                yield retval
