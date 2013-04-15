import unittest

class get_auth_ordersTests(unittest.TestCase):

    def setUp(self):
        from ..models import _session
        self.session = _session

    def tearDown(self):
        self.session.remove()

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
        

        results = list(self._callFUT(shop_id))

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
        

        results = list(self._callFUT(shop_id))

        self.assertEqual(len(results), 0)
