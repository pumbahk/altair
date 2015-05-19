# encoding: utf-8
import unittest

class SalesReportTest(unittest.TestCase):
    def test_basic(self):
        from .sales_report import make_marshaller
        from io import BytesIO
        from datetime import datetime, date
        from decimal import Decimal
        out = BytesIO()
        target = make_marshaller(out, encoding='CP932', eor='\n')
        target({
            'unique_key': u'0',
            'type': 0,
            'management_number': u'0',
            'event_code': u'0',
            'event_code_sub': u'0',
            'acceptance_info_code': 0,
            'performance_code': u'0',
            'event_name': u'イベント名',
            'performance_date': datetime(2015, 1, 1, 0, 0, 0),
            'ticket_price': Decimal(1000),
            'ticketing_fee': Decimal(50),
            'other_fees': Decimal(100),
            'shop': u'0000',
            'settlement_date': date(2015, 1, 1),
            'processed_at': datetime(2015, 1, 1, 0, 0, 0),
            'valid': True,
            'ticket_count': 1,
            'subticket_count': 2,
            })
        self.assertEqual(len(out.getvalue()), 236)
