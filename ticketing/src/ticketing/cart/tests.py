import unittest
from pyramid import testing

def _setup_db():
    import sqlahelper
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    engine.echo = False
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    from . import models
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

    def _add_cart(self, cart_session_id):
        from . import models
        cart = models.Cart(cart_session_id=cart_session_id)
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