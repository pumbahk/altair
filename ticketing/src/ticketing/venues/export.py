# -*- coding: utf-8 -*-
from ticketing.models import record_to_multidict
from ticketing.core.models import SeatStatusEnum

class SeatCSV(object):

    # csv header
    seat_header = [
        'seat_id',
        'seat_no',
        'seat_areas',
        ]
    stock_attribute_header = [
        'floor',
        'gate',
        'row',
        ]
    stock_type_header = [
        'stock_type_id',
        'stock_type_name',
        ]
    stock_holder_header = [
        'stock_holder_id',
        'stock_holder_name',
        ]
    account_header = [
        'account_id',
        'account_name',
        ]
    seat_status_header = [
        'seat_status',
        ]

    def __init__(self, seats):
        self.header = self.seat_header\
                    + self.stock_attribute_header\
                    + self.stock_type_header\
                    + self.stock_holder_header\
                    + self.account_header\
                    + self.seat_status_header
        self.rows = [self._convert_to_csv(seat) for seat in seats]

    def _convert_to_csv(self, seat):
        seat_list = [
            ('seat_id', seat.id),
            ('seat_no', seat.seat_no)
        ]

        stock_attribute_list = []
        for k, v in seat.attributes.items():
            if k in self.stock_attribute_header:
                stock_attribute_list.append((k, v))

        stock_type_list = []
        if seat.stock.stock_holder:
            stock_type_list = [
                ('stock_type_id', seat.stock.stock_type.id),
                ('stock_type_name', seat.stock.stock_type.name)
            ]

        stock_holder_list = []
        if seat.stock.stock_holder:
            stock_holder_list = [
                ('stock_holder_id', seat.stock.stock_holder.id),
                ('stock_holder_name', seat.stock.stock_holder.name)
            ]

        account_list = []
        if seat.stock.stock_holder:
            account_list = [
                ('account_id', seat.stock.stock_holder.account.id),
                ('account_name', seat.stock.stock_holder.account.name)
            ]

        seat_status_list = []
        for status in SeatStatusEnum:
            if status.v == seat.status:
                seat_status_list = [('seat_status', status.k)]
                break

        # encoding
        row = dict(
            seat_list
            + stock_attribute_list
            + stock_type_list
            + stock_holder_list
            + account_list
            + seat_status_list
        )
        for key, value in row.items():
            if value:
                if not isinstance(value, unicode):
                    value = unicode(value)
                value = value.encode('cp932')
            else:
                value = ''
            row[key] = value

        return row
