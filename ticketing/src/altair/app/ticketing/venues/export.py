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

    excluded_order_statuses = ['canceled', 'deleted', 'refunded']

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


        self._seat_status_enum_dict = dict(
            (status.v, status.k) for status in SeatStatusEnum)


    def _convert_to_csv(self, seat_order_pair):
        seat, order = seat_order_pair
        valid_order = order and (order.deleted_at is None) and order.status not in self.excluded_order_statuses
        if (not valid_order) and (seat.id in self.seat_rendered):
            return None
        if seat.id in self.seat_rendered:
            return None
        self.seat_rendered.add(seat.id)
        seat_data = (
            (u'座席ID', seat.id),
            (u'l0_id', seat.l0_id),
            (u'座席番号', seat.seat_no),
            (u'座席名', seat.name),
            (u'フロア', seat.attributes.get('floor', '')),
            (u'ゲート', seat.attributes.get('gate', '')),
            (u'列番号', seat.attributes.get('row', '')),
            (u'座席ステータス', self._seat_status_enum_dict.get(seat.status, '')),
            )

        stock_type_data = ()
        if seat.stock.stock_type:
            stock_type_data = (
                (u'席種ID', seat.stock.stock_type.id),
                (u'席種名', seat.stock.stock_type.name),
                )

        stock_holder_data = ()
        account_data = ()
        if seat.stock.stock_holder:
            stock_holder_data = (
                (u'枠ID', seat.stock.stock_holder.id),
                (u'枠名', seat.stock.stock_holder.name),
                )

            if seat.stock.stock_holder.account:
                account_data = (
                    (u'配券先ID', seat.stock.stock_holder.account.id),
                    (u'配券先名', seat.stock.stock_holder.account.name),
                    )

        order_data = ()
        if valid_order:
            order_data = (
                (u'予約番号', order.order_no if order else ''),
                )

        row =  dict(
            seat_data + \
            stock_type_data + \
            stock_holder_data + \
            account_data + \
            order_data)
        return encode_to_cp932(row)

    @property
    def rows(self):
        for seat_order_pair in self.seat_order_pairs:

            retval = self._convert_to_csv(seat_order_pair)
            if retval is not None:
                yield retval
