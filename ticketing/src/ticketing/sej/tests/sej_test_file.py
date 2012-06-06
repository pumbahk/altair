# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.payment import SejTicketDataXml
from ticketing.sej.utils import JavaHashMap

class SejTest(unittest.TestCase):

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        import sqlahelper
        from sqlalchemy import create_engine
        from ticketing.sej.models import SejOrder
        engine = create_engine("sqlite:///")
        sqlahelper.get_session().remove()
        sqlahelper.add_engine(engine)
        Base = sqlahelper.get_base()
        Base.metadata.create_all()

    def tearDown(self):
        pass

    def test_get_file_payment_request(self):
        import webob.util

        def sej_dummy_response(environ):
            return open(os.path.dirname(__file__)+ '/data/files/SEITIS91_30516_20110912', 'r').read()

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=38004, status=200)
        target.start()

        from ticketing.sej.payment import request_fileget
        from ticketing.sej.resources import SejNotificationType
        from ticketing.sej.file import SejInstantPaymentFileParser
        file = request_fileget(
            date=datetime.datetime(2011,9,12),
            notification_type=SejNotificationType.InstantPaymentInfo,
            hostname=u"http://127.0.0.1:38004")

        target.assert_body("X_shop_id=30520&xcode=4b285c1d4da8c4a7452aec0b0c412c60&X_tuchi_kbn=91&X_date=20110912")
        target.assert_method("POST")

        parser = SejInstantPaymentFileParser()
        data = parser.parse(file)
        assert len(data) == 27

    def test_file_payment(self):
        ''' 入金速報:SEITIS91_30516_20110912
        '''
        import os
        from ticketing.sej.file import SejInstantPaymentFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS91_30516_20110912', 'r').read()
        parser = SejInstantPaymentFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 91
            assert row['payment_type'] == 1 or row['payment_type'] == 2 or \
                    row['payment_type'] == 3 or row['payment_type'] == 4
        assert len(data) == 27

    def test_file_payemnt_expire(self):
        '''支払期限切れ:SEITIS51_30516_20110912'''
        import os
        from ticketing.sej.file import SejExpiredFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS51_30516_20110912', 'r').read()
        parser = SejExpiredFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 51
        assert len(data) == 2

    def test_file_ticketing_expire(self):
        '''発券期限切れ:SEITIS61_30516_201109122'''
        import os
        from ticketing.sej.file import SejExpiredFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS61_30516_20110912', 'r').read()
        parser = SejExpiredFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 61
        assert len(data) == 1

    def test_file_refund(self):
        '''払戻速報:SEITIS92_30516_20110914'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS92_30516_20110914', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 92
        assert len(data) == 4

    def test_file_payment_info(self):
        '''支払い案内:SEITIS94_30516_20111008'''
        import os
        from ticketing.sej.file import SejPaymentInfoFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS94_30516_20111008', 'r').read()
        parser = SejPaymentInfoFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 94
        assert len(data) == 30

    def test_file_check_cancel_pay(self):
        '''□会計取消（入金）:SEITIS95_30516_20110915'''
        import os
        from ticketing.sej.file import SejCheckFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS95_30516_20110915', 'r').read()
        parser = SejCheckFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 95

        assert len(data) == 3

    def test_file_check_cancel_ticketing(self):
        '''□会計取消（発券）:SEITIS96_30516_20110915'''
        import os
        from ticketing.sej.file import SejCheckFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS96_30516_20110915', 'r').read()
        parser = SejCheckFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 96

        assert len(data) == 2

    def test_file_refund_commit(self):
        '''□払戻確定:SEITIS97_30516_20110916'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS97_30516_20110916', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 97
        assert len(data) == 3

    def test_file_refund_cancel(self):
        '''□払戻取消:SEITIS98_30516_20110916'''
        import os
        from ticketing.sej.file import SejRefundFileParser
        body = open(os.path.dirname(__file__)+ '/data/files/SEITIS98_30516_20110916', 'r').read()
        parser = SejRefundFileParser()
        data = parser.parse(body)
        for row in data:
            assert row['notification_type'] == 98

        assert len(data) == 1



if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()