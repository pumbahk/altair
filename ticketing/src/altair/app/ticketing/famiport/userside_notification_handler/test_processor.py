import unittest
import mock
from pyramid.testing import DummyModel
from altair.app.ticketing.testing import DummyRequest
from altair.app.ticketing.core.testing import CoreTestMixin

class AltairFamiPortNotificationProcessorTest(unittest.TestCase, CoreTestMixin):
    def _getTarget(self):
        from .processor import AltairFamiPortNotificationProcessor
        return AltairFamiPortNotificationProcessor

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('altair.app.ticketing.orders.api.get_order_by_order_no')
    def test_regression_12501_1(self, get_order_by_order_no):
        from datetime import datetime
        from ..userside_models import AltairFamiPortNotificationType
        order = get_order_by_order_no.return_value = mock.Mock(paid_at=None)
        request = DummyRequest()
        processor = self._makeOne(request)
        now = datetime(2015, 1, 1)
        processor(
            notification=DummyModel(
                type=AltairFamiPortNotificationType.OrderCanceled.value,
                order_no='XX0000000000'
                ),
            now=now
            )
        order.release.assert_called_with()
        order.mark_canceled.assert_called_with(now)

    @mock.patch('altair.app.ticketing.orders.api.get_order_by_order_no')
    def test_regression_12501_2(self, get_order_by_order_no):
        from datetime import datetime
        from ..userside_models import AltairFamiPortNotificationType
        order = get_order_by_order_no.return_value = mock.Mock(paid_at=datetime(2015, 1, 1))
        request = DummyRequest()
        processor = self._makeOne(request)
        now = datetime(2015, 1, 1)
        processor(
            notification=DummyModel(
                type=AltairFamiPortNotificationType.OrderCanceled.value,
                order_no='XX0000000000'
                ),
            now=now
            )
        order.release.assert_not_called()
        order.mark_canceled.assert_not_called()
