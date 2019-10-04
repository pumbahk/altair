# -*- coding: utf-8 -*-

import mock
import unittest


class IssueNewQrQtrTest(unittest.TestCase):
    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.utils import issue_new_qr_str
        return issue_new_qr_str(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.models.SkidataBarcode.is_barcode_exist')
    def test_success(self, is_barcode_exist):
        """ 正常系テスト コード生成に一発で成功 """
        is_barcode_exist.return_value = False
        qr_str = self._call_test_target()
        self.assertIsNotNone(qr_str)

    @mock.patch('altair.app.ticketing.skidata.models.SkidataBarcode.is_barcode_exist')
    def test_retry_success(self, is_barcode_exist):
        """ 正常系テスト コード生成に数回失敗したのち成功 """
        is_barcode_exist.side_effect = [True, True, False]
        qr_str = self._call_test_target()
        self.assertIsNotNone(qr_str)


class WriteQrImageToStreamTest(unittest.TestCase):
    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.utils import write_qr_image_to_stream
        return write_qr_image_to_stream(*args, **kwargs)

    def test_success(self):
        """ 正常系テスト """
        import StringIO
        test_stream = StringIO.StringIO()
        test_data = u'test'

        self._call_test_target(test_data, test_stream, u'GIF')
        self.assertIsNotNone(test_stream.getvalue())

