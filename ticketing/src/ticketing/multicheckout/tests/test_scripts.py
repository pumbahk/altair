import unittest
from pyramid import testing

class is_cancelableTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..scripts.cancelauth import is_cancelable
        return is_cancelable(*args, **kwargs)

    def test_without_keep(self):
        status = testing.DummyModel(OrderNo='testing',
                                    KeepAuthFor=None)
        request = testing.DummyRequest()
        result = self._callFUT(request, status)
        self.assertTrue(result)

    def test_without_cancel_filter(self):
        status = testing.DummyModel(OrderNo='testing',
                                    KeepAuthFor='testing_order')
        request = testing.DummyRequest()
        result = self._callFUT(request, status)
        self.assertFalse(result)

    def test_with_ok_cancel_filter(self):
        from ..interfaces import ICancelFilter
        filter = DummyCancelFilter(True)
        status = testing.DummyModel(OrderNo='testing',
                                    KeepAuthFor='testing_order')

        self.config.registry.registerUtility(filter, ICancelFilter, name="testing_order")
        request = testing.DummyRequest()
        result = self._callFUT(request, status)
        self.assertTrue(result)


    def test_with_ng_cancel_filter(self):
        from ..interfaces import ICancelFilter
        filter = DummyCancelFilter(False)
        status = testing.DummyModel(OrderNo='testing',
                                    KeepAuthFor='testing_order')

        self.config.registry.registerUtility(filter, ICancelFilter, name="testing_order")
        request = testing.DummyRequest()
        result = self._callFUT(request, status)
        self.assertFalse(result)


class DummyCancelFilter(object):
    def __init__(self, result):
        self.result = result
        self.called = []

    def is_cancelable(self, order_no):
        self.called.append(order_no)
        return self.result

class get_auth_ordersTests(unittest.TestCase):

    def setUp(self):
        import sqlahelper
        from sqlalchemy import create_engine
        from ..models import _session, Base
        engine = create_engine("sqlite:///")
        sqlahelper.add_engine(engine)
        self.session = _session
        self.session.remove()
        self.session.configure(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.config = testing.setUp()

    def tearDown(self):
        self.session.rollback()
        self.session.remove()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..scripts.cancelauth import get_auth_orders
        return get_auth_orders(*args, **kwargs)


    def test_it(self):
        from datetime import datetime, timedelta
        from ..models import (
            MultiCheckoutOrderStatus,
            MultiCheckoutStatusEnum,
        )

        now = datetime.now()
        shop_id="TESTING"

        status = MultiCheckoutOrderStatus(Storecd=shop_id,
                                          Status=unicode(MultiCheckoutStatusEnum.Authorized),
                                          updated_at=now - timedelta(days=1))
        self.session.add(status)
        
        request = testing.DummyRequest()
        results = list(self._callFUT(request, shop_id))

        self.assertEqual(len(results), 1)

    def test_kept(self):
        from datetime import datetime, timedelta
        from ..models import (
            MultiCheckoutOrderStatus,
            MultiCheckoutStatusEnum,
        )

        now = datetime.now()
        shop_id="TESTING"

        status = MultiCheckoutOrderStatus(Storecd=shop_id,
                                          KeepAuthFor=u"testing",
                                          Status=unicode(MultiCheckoutStatusEnum.Authorized),
                                          updated_at=now - timedelta(days=1))
        self.session.add(status)
        

        request = testing.DummyRequest()
        results = list(self._callFUT(request, shop_id))

        self.assertEqual(len(results), 0)

    def test_filtered_cancelable(self):
        from datetime import datetime, timedelta
        from ..interfaces import ICancelFilter
        from ..models import (
            MultiCheckoutOrderStatus,
            MultiCheckoutStatusEnum,
        )
        filter = DummyCancelFilter(True)
        self.config.registry.registerUtility(filter, ICancelFilter, name="testing")

        now = datetime.now()
        shop_id="TESTING"

        status = MultiCheckoutOrderStatus(Storecd=shop_id,
                                          KeepAuthFor=u"testing",
                                          Status=unicode(MultiCheckoutStatusEnum.Authorized),
                                          updated_at=now - timedelta(days=1))
        self.session.add(status)
        

        request = testing.DummyRequest()
        results = list(self._callFUT(request, shop_id))

        self.assertEqual(len(results), 1)
