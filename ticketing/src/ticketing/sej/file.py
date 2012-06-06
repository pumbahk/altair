# -*- coding:utf-8 -*-

import logging
from dateutil import parser
logger = logging.getLogger(__file__)

class SejFileParser(object):

    class SejFileParserRow(object):
        cursor = 0
        #
        def __init__(self, row):
            self.row = row
        #
        def get_col(self, num):
            row = self.row[self.cursor:self.cursor+num]
            self.cursor = self.cursor + num
            return row

        def get_int(self, num):
            col = self.get_col(num).replace(' ', '')
            return int(col) if len(col) else None

        def get_datetime(self, num):
            col = self.get_col(num).replace(' ', '')
            return parser.parse(col) if len(col) else None

    rec_segment = ''
    shop_id     = ''
    filename    = ''
    date        = ''
    row_length  = 0
    row_count   = 0

    def parse_header(self, row):
        self.rec_segment = row.get_col(1)
        if self.rec_segment != 'H':
            raise Exception("Invalid header type : %s" % self.rec_segment)
        self.shop_id     = row.get_col(5)
        self.filename    = row.get_col(30)
        self.date        = row.get_col(8)
        self.row_length  = int(row.get_col(4))

    def parse_footer(self, row):
        self.row_count   = int(row.get_col(6))

    def parse_row(self, row):
        raise Exception("stub: method not implements.")

    def parse(self, data):

        self.parse_header(SejFileParser.SejFileParserRow(data))
        total_length = len(data)

        if total_length % self.row_length != 0:
            raise Exception('Invalid row length  row:%d total:%d' % (self.row_length, total_length))

        values = []

        for start_at in range(self.row_length, len(data),self.row_length):
            row = data[start_at : start_at + self.row_length]
            row_obj = SejFileParser.SejFileParserRow(row)
            row_type = row_obj.get_col(1)
            if row_type == 'E':
                self.parse_footer(row_obj)
                break
            values.append(self.parse_row(row_obj))

        if not self.row_count:
            raise Exception('Invalid row footer row:%d total:%d' % (self.row_length, total_length))
        if self.row_count != len(values)+2:
            raise Exception('Invalid row count count:%d/%d row:%d total:%d' % (self.row_count, len(values), self.row_length, total_length))

        return values


class SejInstantPaymentFileParser(SejFileParser):

    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            shop_id             = row.get_col(5),
            order_id            = row.get_col(12),
            notification_type   = row.get_int(2),
            payment_type        = row.get_int(2),
            bill_number         = row.get_col(13).strip(),
            exchange_number     = row.get_col(13),
            price               = row.get_int(6),
            ticket_total_count  = row.get_col(2),
            ticket_count        = row.get_int(2),
            return_ticket_coun  = row.get_int(2),
            cancel_reason       = row.get_col(2),
            process_at          = row.get_datetime(14),
            checksum            = row.get_col(32)
        )
        return data

class SejExpiredFileParser(SejFileParser):
    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            shop_id             = row.get_col(5),
            order_id            = row.get_col(12),
            notification_type   = row.get_int(2),
            payment_type        = row.get_int(2),
            expired_at          = row.get_datetime(12),
            bill_number         = row.get_col(13),
            exchange_number     = row.get_col(13),
            checksum            = row.get_col(32),
        )
        return data

class SejPaymentInfoFileParser(SejFileParser):
    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            notification_type   = row.get_int(2),
            ticket_barcode_number
                                = row.get_col(13),
            order_id            = row.get_col(12),
            credit_price        = row.get_col(6),
            recieved_at         = row.get_datetime(14),
            close_at            = row.get_datetime(14),
            pay_at              = row.get_datetime(14),
            payment_for         = row.get_int(2),
        )
        return data


class SejRefundFileParser(SejFileParser):

    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            notification_type   = int(row.get_col(2)),
            ticket_barcode_number
                                = row.get_col(13),
            order_id            = row.get_col(12),
            refund_ticket_price = row.get_int(6),
            refund_other_price  = row.get_int(6),
            received_at         = row.get_datetime(14),
            payment_type        = row.get_int(2),
            refund_status       = row.get_int(2), # 01:払戻済み 02:払戻取消
            refund_cancel_reason= row.get_int(2), # 02:払戻取消のとき
            refund_cancel_at    = row.get_datetime(14)
        )
        return data

class SejCheckFileParser(SejFileParser):
    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            shop_id             = row.get_col(5),
            order_id            = row.get_col(12),
            notification_type   = int(row.get_col(2)),
            payment_type        = row.get_int(2),
            billing_number      = row.get_col(13),
            exchnage_number     = row.get_col(13),
            receipt_amount      = row.get_int(6),
            ticket_total_count  = row.get_int(2),
            ticket_count        = row.get_int(2),
            return_count        = row.get_int(2),
            cancel_reason       = row.get_int(2),
            process_at         = row.get_datetime(14),
        )
        return data

class SejRefundFileParser(SejFileParser):
    def parse_row(self, row):
        data = dict(
            segment             = 'D',
            notification_type   = int(row.get_col(2)),
            ticket_barcode_number
                                = row.get_col(13),
            order_id            = row.get_col(12),
            ticket_refund_amount= row.get_int(6),
            other_refund_amount = row.get_int(6),
            recieved_at         = row.get_datetime(14),
            payment_type        = row.get_int(2),
            refund_status       = row.get_int(2),
            refund_reason       = row.get_int(2),
            refund_at           = row.get_datetime(14),

        )
        return data
