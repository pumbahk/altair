import unittest
from pyramid import testing

def _setup_db():
    import sqlahelper
    from sqlalchemy import create_engine
    from . import models
    import ticketing.venues.models
    import ticketing.products.models
    import ticketing.events.models
    import ticketing.orders.models

    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return sqlahelper.get_session()



class CartTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.Cart

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_cart(self, cart_session_id, created_at=None):
        from datetime import datetime
        from . import models
        if created_at is None:
            created_at = datetime.now()
        cart = models.Cart(cart_session_id=cart_session_id, created_at=created_at)
        self.session.add(cart)
        return cart

    def test_is_existing_cart_session_id_not_exsiting(self):
        target = self._getTarget()

        result = target.is_existing_cart_session_id(u"x")

        self.assertFalse(result)

    def test_is_existing_cart_session_id_exsiting(self):
        self._add_cart(u"x")
        target = self._getTarget()

        result = target.is_existing_cart_session_id(u"x")

        self.assertTrue(result)

    def test_is_expired_instance_expired(self):
        from datetime import datetime, timedelta
        created = datetime.now() - timedelta(minutes=16)
        target = self._makeOne(created_at=created)
        result = target.is_expired(15)
        self.assertFalse(result)

    def test_is_expired_instance(self):
        from datetime import datetime, timedelta
        created = datetime.now() - timedelta(minutes=14)
        target = self._makeOne(created_at=created)
        result = target.is_expired(15)
        self.assertTrue(result)

    def test_is_expired_class(self):
        from datetime import datetime, timedelta
        valid_created = datetime.now() - timedelta(minutes=14)
        expired_created = datetime.now() - timedelta(minutes=16)
        self._add_cart(u"valid", created_at=valid_created)
        self._add_cart(u"expired", created_at=expired_created)

        target = self._getTarget()
        result = target.query.filter(target.is_expired(expire_span_minutes=15)).all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cart_session_id, u'valid')

class CartedProductTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        import transaction
        transaction.abort()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartedProduct

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


class TicketingCartResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        import transaction
        transaction.abort()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import resources
        return resources.TicketingCartResrouce

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_stock_status(self, quantity=100):
        from ..products import models
        product_item = models.ProductItem(id=1)
        stock = models.Stock(id=1, product_items=[product_item])
        stock_status = models.StockStatus(stock=stock, quantity=quantity)
        models.DBSession.add(stock_status)
        return product_item

    def test_get_stock_status(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        product_item = self._add_stock_status()
        result = target.get_stock_status(product_item.id)

        self.assertIsNotNone(result)

    def test_has_stock_just_quantity(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        product_item = self._add_stock_status(quantity=100)
        result = target.has_stock(product_item.id, 100)

        self.assertTrue(result)

    def test_has_stock_1_less(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        product_item = self._add_stock_status(quantity=99)
        result = target.has_stock(product_item.id, 100)

        self.assertFalse(result)

    def test_has_stock_1_greater(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        product_item = self._add_stock_status(quantity=100)
        result = target.has_stock(product_item.id, 99)

        self.assertTrue(result)