# -*- coding:utf-8 -*-

import logging
from dateutil.parser import parse as parsedate
from .models import SejNotificationType
from collections import OrderedDict

logger = logging.getLogger(__file__)

class SejFileParserError(Exception):
    pass

class SejFileReader(object):
    def get_col_raw(self, num):
        retval = self.f.read(num)
        if len(retval) != num:
            raise SejFileParserError("Unexpected EOF")
        self.cursor += num
        return retval

    def get_col(self, num):
        return self.get_col_raw(num).decode(self.encoding)

    def get_col_strip(self, num):
        return self.get_col_raw(num).replace(' ', '').decode(self.encoding)

    def get_int(self, num):
        col = self.get_col_strip(num)
        return int(col) if col else None

    def get_datetime(self, num):
        col = self.get_col_strip(num)
        return parsedate(col) if len(col) else None

    def eor(self):
        if self.cursor > self.record_length:
            raise SejFileParserError('cursor overrun (%d >= %d)' % (self.cursor, self.record_length))
        self.f.read(self.record_length - self.cursor)
        self.cursor = 0

    def __init__(self, f, encoding='CP932'):
        self.f = f
        self.encoding = encoding
        self.cursor = 0
        self.record_length = 0

class SejFileParser(object):
    rec_segment = ''
    shop_id     = ''
    filename    = ''
    date        = ''

    def __init__(self, reader):
        self.reader = reader
        self.shop_id     = None
        self.filename    = None
        self.date        = None
        self.records     = []

    def header(self):
        self.shop_id     = self.reader.get_col(5)
        self.filename    = self.reader.get_col_strip(30)
        self.date        = self.reader.get_datetime(8)
        self.reader.record_length = self.reader.get_int(4)
        self.reader.eor()

    def footer(self):
        expected_record_count = int(self.reader.get_col(6)) - 2
        self.reader.eor()
        if len(self.records) != expected_record_count:
            raise SejFileParserError("record count mismatch: expected %d, actual %d" % (expected_record_count, len(self.records)))

    def parse_row(self, row):
        raise NotImplementedError("stub: method not implements.")

    def parse(self):
        try:
            row_type = self.reader.get_col(1)

            if row_type != 'H':
                raise SejFileParserError("Unknown row type: %s" % row_type)
        except SejFileParserError:
            return False # EOF
            
        self.header()

        while True:
            row_type = self.reader.get_col(1)
            if row_type == 'E':
                self.footer()
                break
            elif row_type == 'D':
                record = self.parse_row()
                self.reader.eor()
                self.records.append(record)
            else:
                raise SejFileParserError("Unknown row type: %s" % row_type)

        return True

class SejInstantPaymentFileParser(SejFileParser):
    notification_types = [SejNotificationType.FileInstantPaymentInfo]

    def parse_row(self):
        return OrderedDict([
            ('shop_id'               , self.reader.get_col(5)),
            ('order_id'              , self.reader.get_col(12)),
            ('notification_type'     , self.reader.get_int(2)),
            ('payment_type'          , self.reader.get_int(2)),
            ('billing_number'        , self.reader.get_col_strip(13)),
            ('exchange_number'       , self.reader.get_col_strip(13)),
            ('price'                 , self.reader.get_int(6)),
            ('total_ticket_count'    , self.reader.get_col(2)),
            ('ticket_count'          , self.reader.get_int(2)),
            ('return_ticket_count'   , self.reader.get_int(2)),
            ('cancel_reason'         , self.reader.get_col(2)),
            ('process_at'            , self.reader.get_datetime(14)),
            ('signature'             , self.reader.get_col(32))
            ])

class SejExpireFileParser(SejFileParser):
    notification_types = [
        SejNotificationType.FilePaymentExpire,
        SejNotificationType.FileTicketingExpire
        ]
    def parse_row(self):
        return OrderedDict([
            ('shop_id'               , self.reader.get_col(5)),
            ('order_id'              , self.reader.get_col(12)),
            ('notification_type'     , self.reader.get_int(2)),
            ('payment_type'          , self.reader.get_int(2)),
            ('expired_at'            , self.reader.get_datetime(12)),
            ('billing_number'        , self.reader.get_col(13)),
            ('exchange_number'       , self.reader.get_col(13)),
            ('checksum'              , self.reader.get_col(32)),
            ])

class SejPaymentInfoFileParser(SejExpireFileParser):
    notification_types = [ SejNotificationType.FileCheckInfo ]
    def parse_row(self):
        return OrderedDict([
            ('notification_type'     , self.reader.get_int(2)),
            ('ticket_barcode_number' , self.reader.get_col(13)),
            ('order_id'              , self.reader.get_col(12)),
            ('credit_price'          , self.reader.get_col(6)),
            ('recieved_at'           , self.reader.get_datetime(14)),
            ('close_at'              , self.reader.get_datetime(14)),
            ('pay_at'                , self.reader.get_datetime(14)),
            ('payment_for'           , self.reader.get_int(2))
            ])

class SejRefundFileParser(SejFileParser):
    notification_types = [
        SejNotificationType.FileInstantRefundInfo,
        SejNotificationType.FileRefundComplete,
        SejNotificationType.FileRefundCancel,
        ]

    def parse_row(self):
        return OrderedDict([
            ('notification_type'     , self.reader.get_int(2)),
            ('ticket_barcode_number' , self.reader.get_col(13)),
            ('order_id'              , self.reader.get_col(12)),
            ('refund_ticket_price'   , self.reader.get_int(6)),
            ('refund_other_price'    , self.reader.get_int(6)),
            ('received_at'           , self.reader.get_datetime(14)),
            ('payment_type'          , self.reader.get_int(2)),
            ('refund_status'         , self.reader.get_int(2)), # 01:払戻済み 02:払戻取消
            ('refund_cancel_reason'  , self.reader.get_int(2)), # 02:払戻取消のとき
            ('refund_cancel_at'      , self.reader.get_datetime(14))
            ])

class SejCheckFileParser(SejFileParser):
    notification_types = [
        SejNotificationType.FilePaymentCancel,
        SejNotificationType.FileTicketingCancel,
        ]

    def parse_row(self):
        return OrderedDict([
            ('shop_id'               , self.reader.get_col(5)),
            ('order_id'              , self.reader.get_col(12)),
            ('notification_type'     , self.reader.get_int(2)),
            ('payment_type'          , self.reader.get_int(2)),
            ('billing_number'        , self.reader.get_col_strip(13)),
            ('exchnage_number'       , self.reader.get_col_strip(13)),
            ('receipt_amount'        , self.reader.get_int(6)),
            ('ticket_total_count'    , self.reader.get_int(2)),
            ('ticket_count'          , self.reader.get_int(2)),
            ('return_count'          , self.reader.get_int(2)),
            ('cancel_reason'         , self.reader.get_int(2)),
            ('process_at'            , self.reader.get_datetime(14))
            ])

parsers = [
    SejInstantPaymentFileParser,
    SejExpireFileParser,
    SejPaymentInfoFileParser,
    SejRefundFileParser,
    SejCheckFileParser,
    ]

