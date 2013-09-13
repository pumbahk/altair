import unittest
from pyramid import testing


class is_finished_deliveryTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from ..api import is_finished_delivery
        return is_finished_delivery(*args, **kwargs)

    def test_no_order(self):
        request = testing.DummyRequest()
        pdmp = testing.DummyModel()
        order = None

        result = self._callFUT(request, pdmp, order)

        self.assertFalse(result)

    def test_plugin_no_finished(self):
        from ..interfaces import IDeliveryPlugin
        class DummyDeliveryPlugin(testing.DummyResource):
            def finished(self, request, order):
                return False
        dummy_delivery_plugin = DummyDeliveryPlugin()

        request = testing.DummyRequest()
        self.config.registry.utilities.register([], IDeliveryPlugin, "delivery-9999",
                                                dummy_delivery_plugin)
        pdmp = testing.DummyModel(
            delivery_method=testing.DummyModel(
                delivery_plugin_id=9999,
            ),
        )
        order = testing.DummyModel()

        result = self._callFUT(request, pdmp, order)

        self.assertFalse(result)

    def test_plugin_finished(self):
        from ..interfaces import IDeliveryPlugin
        class DummyDeliveryPlugin(testing.DummyResource):
            def finished(self, request, order):
                return True
        dummy_delivery_plugin = DummyDeliveryPlugin()

        request = testing.DummyRequest()
        self.config.registry.utilities.register([], IDeliveryPlugin, "delivery-9999",
                                                dummy_delivery_plugin)
        pdmp = testing.DummyModel(
            delivery_method=testing.DummyModel(
                delivery_plugin_id=9999,
            ),
        )
        order = testing.DummyModel()

        result = self._callFUT(request, pdmp, order)

        self.assertTrue(result)
