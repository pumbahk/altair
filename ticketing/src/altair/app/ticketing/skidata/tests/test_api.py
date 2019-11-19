# -*- coding: utf-8 -*-

import unittest
import mock
from pyramid.testing import DummyModel


class CreateNewBarcodeTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import create_new_barcode
        return create_new_barcode(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_create_new_barcode_success(self, find_all_by_order_no, insert_new_barcode):
        """ create_new_barcodeの正常系テスト """
        find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        self.__call_test_target(order_no='TEST0000001')
        self.assertTrue(insert_new_barcode.called)
