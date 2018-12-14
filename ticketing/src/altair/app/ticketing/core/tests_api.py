# encoding: utf-8

import unittest
from pyramid.testing import DummyModel, setUp, tearDown
from altair.app.ticketing.testing import DummyRequest
from altair.mobile.api import detect_from_email_address


class GetDefaultContactUrlTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getTarget(self):
        from .api import get_default_contact_url
        return get_default_contact_url


    def setUp(self):
        request = DummyRequest()
        config = setUp(request=request)
        config.include('altair.mobile')
        self.request = request

    def tearDown(self):
        tearDown()

    def test_both_specified_pc(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/pc')

    def test_both_specified_mobile(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/mobile')

    def test_either_specified_pc_1(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/pc')

    def test_either_specified_pc_2(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url='http://example.com/contact/pc',
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_either_specified_mobile_1(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_either_specified_mobile_2(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url='http://example.com/contact/mobile',
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'http://example.com/contact/mobile')

    def test_none_specified_pc(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@example.com')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')

    def test_none_specified_mobile(self):
        organization = DummyModel(
            setting = DummyModel(
                contact_pc_url=None,
                contact_mobile_url=None,
                default_mail_sender='default@example.com'
                )
            )
        ua = detect_from_email_address(self.request.registry, 'a@docomo.ne.jp')
        result = self._callFUT(self.request, organization, ua)
        self.assertEquals(result, 'mailto:default@example.com')


class GetPointUseTypeFromOrderLike(unittest.TestCase):
    def _call_test_target(self, *args, **kwargs):
        from .api import get_point_use_type_from_order_like
        return get_point_use_type_from_order_like(*args, **kwargs)

    def test_point_no_use(self):
        """
        ポイント利用なしのパターン
        """
        from .models import PointUseTypeEnum
        order_like = DummyModel(
            total_amount=1000,
            point_amount=0,
        )
        point_use_type = self._call_test_target(order_like)
        self.assertEqual(point_use_type, PointUseTypeEnum.NoUse)

    def test_point_partial_use(self):
        """
        一部ポイント払いのパターン
        """
        from .models import PointUseTypeEnum
        order_like = DummyModel(
            total_amount=1000,
            point_amount=100,
        )
        point_use_type = self._call_test_target(order_like)
        self.assertEqual(point_use_type, PointUseTypeEnum.PartialUse)

    def test_point_partial_use_with_point_amount_of_all_use(self):
        """
        一部ポイント払い、point_amount_of_all_use指定のパターン
        """
        from .models import PointUseTypeEnum
        order_like = DummyModel(
            total_amount=1000,
            point_amount=100,
        )
        point_amount_of_all_use = 500
        point_use_type = self._call_test_target(order_like, point_amount_of_all_use)
        self.assertEqual(point_use_type, PointUseTypeEnum.PartialUse)

    def test_point_all_use(self):
        """
        全額ポイント払いのパターン
        """
        from .models import PointUseTypeEnum
        order_like = DummyModel(
            total_amount=1000,
            point_amount=1000,
        )
        point_use_type = self._call_test_target(order_like)
        self.assertEqual(point_use_type, PointUseTypeEnum.AllUse)

    def test_point_all_use_with_point_amount_of_all_use(self):
        """
        全額ポイント払い、point_amount_of_all_use指定のパターン
        """
        from .models import PointUseTypeEnum
        order_like = DummyModel(
            total_amount=1000,
            point_amount=100,
        )
        point_amount_of_all_use = 100
        point_use_type = self._call_test_target(order_like, point_amount_of_all_use)
        self.assertEqual(point_use_type, PointUseTypeEnum.AllUse)
