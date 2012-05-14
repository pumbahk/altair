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

        result = target.is_existing_cart_session_id("x")

        self.assertFalse(result)

    def test_is_existing_cart_session_id_exsiting(self):
        self._add_cart("x")
        target = self._getTarget()

        result = target.is_existing_cart_session_id("x")

        self.assertTrue(result)

class CartItemTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        import transaction
        transaction.abort()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_reserved_amount_empty(self):
        target = self._getTarget()
        from ticketing.products import models as p_models
        product_item = p_models.ProductItem()
        result = target.get_reserved_amount(product_item)
        self.assertEqual(result, 0)

    def test_reserved_amount(self):
        target = self._getTarget()
        from ticketing.products import models as p_models
        product_item = p_models.ProductItem(id=1)
        self.session.add(target(product_item=product_item, amount=10, state="reserved"))

        result = target.get_reserved_amount(product_item)
        self.assertEqual(result, 10)

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

    def test_has_stock_without_reserved_having(self):
        from ticketing.products import models as p_models
        stock = p_models.Stock(id=1, quantity=100)
        product_item = p_models.ProductItem(id=1, stock=stock)
        self.session.add(product_item)

        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.has_stock(10, product_item)

        self.assertTrue(result)

    def test_has_stock_without_reserved_not_having(self):
        from ticketing.products import models as p_models
        stock = p_models.Stock(id=1, quantity=100)
        product_item = p_models.ProductItem(id=1, stock=stock)
        self.session.add(product_item)

        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.has_stock(101, product_item)

        self.assertFalse(result)

    def test_has_stock_wit_reserved_not_having(self):
        from ticketing.products import models as p_models
        stock = p_models.Stock(id=1, quantity=100)
        product_item = p_models.ProductItem(id=1, stock=stock)
        self.session.add(product_item)
        from . import models as m
        cart_item = m.CartItem(product_item=product_item, state="reserved", amount=10)
        self.session.add(cart_item)

        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.has_stock(91, product_item)

        self.assertFalse(result)
