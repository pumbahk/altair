# -*- coding:utf-8 -*-
from altair.app.ticketing import testing
from datetime import datetime
from pyramid.decorator import reify
import unittest

_i = 0
def gensym():
    global _i
    _i = _i+1
    return unicode(_i)

def setup_order(gensym=gensym):
    from altair.app.ticketing.core.models import Order
    return Order(
        shipping_address_id=-1, #xxx:
        total_amount=600, 
        system_fee=100, 
        transaction_fee=200, 
        delivery_fee=300, 
        special_fee=400, 
        multicheckout_approval_no=":multicheckout_approval_no", 
        order_no=gensym(), 
        paid_at=datetime(2000, 1, 1, 1, 10), 
        delivered_at=None, 
        canceled_at=None, 
        created_at=datetime(2000, 1, 1, 1), 
        issued_at=datetime(2000, 1, 1, 1, 13),
        organization_id=-1, 
        payment_delivery_method_pair_id=-1, 
        performance_id=-1, 
    )

class AttributesManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        testing._setup_db(["altair.app.ticketing.core.models"])
        import transaction
        transaction.abort()

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()
        testing._teardown_db()

    def tearDown(self):
        import transaction
        transaction.commit() #we needs Integrity Error. if Dupplicated Entry is found.

    @reify
    def order(self):
        from altair.app.ticketing.models import DBSession
        order = setup_order()
        DBSession.add(order)
        return order

    def refreshed_order(self):
        from altair.app.ticketing.models import DBSession
        return DBSession.merge(self.order)

    def _getTarget(self):
        from altair.app.ticketing.core.modelmanage import OrderAttributeManager
        return OrderAttributeManager

    # def test_why_need_this(self):
    #     order = self.order
    #     order.attributes[u"あ"] = "v"
    #     import transaction
    #     transaction.commit()

    #     order = self.refreshed_order()
    #     order.attributes[u"あ".encode("utf-8")] = "v2"

    def test_create(self):
        data = {u"あ": "v"}
        result = self._getTarget().update(self.order, data, encoding="utf-8")
        self.assertEquals(result.attributes, {u"あ": "v"})

    def test_update_another(self):
        import transaction

        data = {u"あ": "v"}
        self._getTarget().update(self.order, data, encoding="utf-8")
        transaction.commit()
        
        order = self.refreshed_order()
        data = {u"あ2": "v2"}
        result = self._getTarget().update(order, data)
        self.assertEquals(result.attributes, {u"あ": "v", u"あ2": "v2"})

    def test_update_same_key(self):
        import transaction

        data = {u"あ": "v"}
        self._getTarget().update(self.order, data, encoding="utf-8")
        transaction.commit()
        
        order = self.refreshed_order()
        data = {u"あ": "v2"}
        result = self._getTarget().update(order, data)
        self.assertEquals(result.attributes, {u"あ": "v2"})

    def test_update_same_key__not_unicode(self):
        import transaction

        data = {u"あ": "v"}
        self._getTarget().update(self.order, data, encoding="utf-8")
        transaction.commit()
        
        order = self.refreshed_order()
        data = {u"あ".encode("utf-8"): "v2"}
        result = self._getTarget().update(order, data)
        self.assertEquals(result.attributes, {u"あ": "v2"})

    def test_update_drop_item(self):
        import transaction

        data = {u"あ": "v"}
        self._getTarget().update(self.order, data, encoding="utf-8")
        transaction.commit()
        
        order = self.refreshed_order()
        data = {u"あ": ""}
        result = self._getTarget().update(order, data, blank_value="")
        self.assertEquals(result.attributes, {})

    def test_create_with_blank_value(self):
        import transaction

        data = {}
        self._getTarget().update(self.order, data, encoding="utf-8")
        transaction.commit()
        
        order = self.refreshed_order()
        data = {u"あ": ""}
        result = self._getTarget().update(order, data, blank_value="")
        self.assertEquals(result.attributes, {})
