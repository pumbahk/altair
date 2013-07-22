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

    def __init__(self, seats):
        self.header = self.seat_header.values()\
                    + self.stock_attribute_header.values()\
                    + self.stock_type_header.values()\
                    + self.stock_holder_header.values()\
                    + self.account_header.values()\
                    + self.seat_status_header.values()
        self.header = [column.encode('cp932') for column in self.header]
        self.rows = [self._convert_to_csv(seat) for seat in seats]

    def get_row_data(self, header, data):
        data = record_to_multidict(data)
        return [(label, data.get(column)) for column, label in header.items()]

    def add_row_data(self, header, data):
        self.row_data += self.get_row_data(header, data)

    def _convert_to_csv(self, seat):
        self.row_data = []

        self.add_row_data(self.seat_header, seat)
        if seat.stock.stock_type:
            self.add_row_data(self.stock_type_header, seat.stock.stock_type)
        if seat.stock.stock_holder:
            self.add_row_data(self.stock_holder_header, seat.stock.stock_holder)
            if seat.stock.stock_holder.account:
                self.add_row_data(self.account_header, seat.stock.stock_holder.account)

        for k, v in seat.attributes.items():
            if k in self.stock_attribute_header:
                label = self.stock_attribute_header.get(k)
                self.row_data.append((label, v))

        for status in SeatStatusEnum:
            if status.v == seat.status:
                label = self.seat_status_header.get('status')
                self.row_data.append((label, status.k))
                break
        if seat.ordered_product_items:
            for opi in seat.ordered_product_items:
                if opi.ordered_product.order.status not in ('canceled'):
                    label = self.seat_status_header.get('order_no')
                    self.row_data.append((label, opi.ordered_product.order.order_no))
                    break

        # encoding
        row = dict(self.row_data)
        return encode_to_cp932(row)
