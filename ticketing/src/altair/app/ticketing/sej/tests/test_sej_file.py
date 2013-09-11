# -*- coding:utf-8 -*-
import unittest
import datetime
import os

from ..ticket import SejTicketDataXml
from ..utils import JavaHashMap

class SejTestFile(unittest.TestCase):
    def setUp(self):
        import sqlahelper
        from sqlalchemy import create_engine
        from ..models import SejOrder
        engine = create_engine("sqlite:///")
        sqlahelper.get_session().remove()
        sqlahelper.add_engine(engine)
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

    def tearDown(self):
        pass

    def _openTestDataFile(self, file_):
        return open(os.path.join(os.path.dirname(__file__), 'data', 'files', file_), 'r')

    def _makeReader(self, file_):
        from ..file import SejFileReader
        return SejFileReader(self._openTestDataFile(file_))

    def test_get_file_payment_request(self):
        import webob.util
        from zlib import compress, decompress
        from .webapi import DummyServer
        from ..file import SejFileReader
        from cStringIO import StringIO

        def sej_dummy_response(environ):
            return compress(self._openTestDataFile('SEITIS91_30516_20110912').read())

        dummy_server = DummyServer(sej_dummy_response, host='127.0.0.1', port=18090, status=800)
        dummy_server.start()
        try:

            webob.util.status_reasons[800] = 'OK'

            from ..payment import request_fileget
            from ..resources import SejNotificationType
            from ..file import SejInstantPaymentFileParser
            file = request_fileget(
                date=datetime.datetime(2011,9,12),
                notification_type=SejNotificationType.InstantPaymentInfo,
                hostname=u"http://127.0.0.1:18090")
            dummy_server.poll()
            self.assertEqual(dummy_server.request.body, "X_shop_id=30520&xcode=71493542957ed71cc35e0f8810e018a9&X_data_type=91&X_date=20110912")
            self.assertEqual(dummy_server.request.method, "POST")

            parser = SejInstantPaymentFileParser(SejFileReader(StringIO(file)))
            parser.parse()
            assert len(parser.records) == 27
        finally:
            dummy_server.stop()

    def test_file_payment(self):
        ''' 入金速報:SEITIS91_30516_20110912
        '''
        from ..file import SejInstantPaymentFileParser
        parser = SejInstantPaymentFileParser(self._makeReader('SEITIS91_30516_20110912'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 91
            assert row['payment_type'] == 1 or row['payment_type'] == 2 or \
                    row['payment_type'] == 3 or row['payment_type'] == 4
        assert len(parser.records) == 27

    def test_file_payemnt_expire(self):
        '''支払期限切れ:SEITIS51_30516_20110912'''
        from ..file import SejExpireFileParser
        parser = SejExpireFileParser(self._makeReader('SEITIS51_30516_20110912'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 51
        assert len(parser.records) == 2

    def test_file_ticketing_expire(self):
        '''発券期限切れ:SEITIS61_30516_201109122'''
        from ..file import SejExpireFileParser
        parser = SejExpireFileParser(self._makeReader('SEITIS61_30516_20110912'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 61
        assert len(parser.records) == 1

    def test_file_refund(self):
        '''払戻速報:SEITIS92_30516_20110914'''
        from ..file import SejRefundFileParser
        parser = SejRefundFileParser(self._makeReader('SEITIS92_30516_20110914'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 92
        assert len(parser.records) == 4

    def test_file_payment_info(self):
        '''支払い案内:SEITIS94_30516_20111008'''
        from ..file import SejPaymentInfoFileParser
        parser = SejPaymentInfoFileParser(self._makeReader('SEITIS94_30516_20111008'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 94
        assert len(parser.records) == 30

    def test_file_check_cancel_pay(self):
        '''会計取消（入金）:SEITIS95_30516_20110915'''
        from ..file import SejCheckFileParser
        parser = SejCheckFileParser(self._makeReader('SEITIS95_30516_20110915'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 95

        assert len(parser.records) == 3

    def test_file_check_cancel_ticketing(self):
        '''□会計取消（発券）:SEITIS96_30516_20110915'''
        from ..file import SejCheckFileParser
        parser = SejCheckFileParser(self._makeReader('SEITIS96_30516_20110915'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 96

        assert len(parser.records) == 2

    def test_file_refund_commit(self):
        '''□払戻確定:SEITIS97_30516_20110916'''
        from ..file import SejRefundFileParser
        parser = SejRefundFileParser(self._makeReader('SEITIS97_30516_20110916'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 97
        assert len(parser.records) == 3

    def test_file_refund_cancel(self):
        '''□払戻取消:SEITIS98_30516_20110916'''
        import os
        from ..file import SejRefundFileParser
        parser = SejRefundFileParser(self._makeReader('SEITIS98_30516_20110916'))
        parser.parse()
        for row in parser.records:
            assert row['notification_type'] == 98

        assert len(parser.records) == 1



if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()
