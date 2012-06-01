# -*- coding:utf-8 -*-

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

def _teardown_db():
    import transaction
    transaction.abort()

class CartTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
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

    def test_total_amount_empty(self):
        target = self._makeOne()
        self.assertEqual(target.total_amount, 0)

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

    def test_add_seats(self):
        ordered_products = [(testing.DummyResource(id=i, items=[
            testing.DummyResource(stock_id=1),
        ]), 1) for i in range(10)]
        seats = [testing.DummyResource(id=i, stock_id=1) for i in range(10)]
        target = self._makeOne()
        target.add_seat(seats, ordered_products)

        self.assertEqual(target.products[0].product.id, 0)
        self.assertEqual(target.products[0].quantity, 1)
        self.assertEqual(len(target.products[0].items), 1)

class CartedProductTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartedProduct

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_pop_seats(self):
        product = testing.DummyResource(items=[testing.DummyResource(stock_id=2),
                                               testing.DummyResource(stock_id=3)])
        target = self._makeOne(id=1, product=product, quantity=1)
        result = target.pop_seats([testing.DummyResource(stock_id=1),
                                   testing.DummyResource(stock_id=2),
                                   testing.DummyResource(stock_id=3)])

        self.assertEqual(len(target.items), 2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].stock_id, 1)


class CartedProductItemTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_pop_seats(self):
        product_item = testing.DummyResource(stock_id=2)
        target = self._makeOne(id=1, product_item=product_item, quantity=2)
        result = target.pop_seats([testing.DummyResource(stock_id=1),
                                   testing.DummyResource(stock_id=2),
                                   testing.DummyResource(stock_id=2),
                                   testing.DummyResource(stock_id=3),
                                   testing.DummyResource(stock_id=2)])

        self.assertEqual(len(target.seats), 2)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].stock_id, 1)
        self.assertEqual(result[1].stock_id, 3)
        self.assertEqual(result[2].stock_id, 2)


class TicketingCartResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import resources
        return resources.TicketingCartResrouce

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_stock_status(self, quantity=100):
        from ..products import models
        product_item = models.ProductItem(id=1, price=0, quantity=0)
        stock = models.Stock(id=1, product_items=[product_item])
        stock_status = models.StockStatus(stock=stock, quantity=quantity)
        models.DBSession.add(stock_status)
        return product_item

    def test_convert_order_product_items(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)

        products = [(testing.DummyResource(items=[testing.DummyResource() for j in range(2)]), i) for i in range(5)]
        result = list(target._convert_order_product_items(products))

        self.assertEqual(len(result), 10)
        self.assertEqual(result[0][1], 0)
        self.assertEqual(result[5][1], 2)
        self.assertEqual(result[9][1], 4)

    def test_quantity_for_stock_id(self):
        import random

        ordered_products = [
            # 大人 S席
            (testing.DummyResource(items=[testing.DummyResource(stock_id=1)]), 2),
            # 子供 S席
            (testing.DummyResource(items=[testing.DummyResource(stock_id=1)]), 3),
            # 大人 S席 + 駐車場
            (testing.DummyResource(items=[testing.DummyResource(stock_id=1),
                                          testing.DummyResource(stock_id=2)]), 1),
            ]

        random.shuffle(ordered_products)
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = list(target.quantity_for_stock_id(ordered_products))

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (1, 6))
        self.assertEqual(result[1], (2, 1))

    def test_order_products_empty(self):
        request = testing.DummyRequest()

        target = self._makeOne(request)

        ordered_products = []
        cart = target.order_products(ordered_products)

        self.assertIsNotNone(cart)
        self.assertEqual(len(cart.products), 0)

    def _add_venue(self, organization_id, site_id, venue_id):
        from ticketing.venues.models import Venue, Site
        from ticketing.organizations.models import Organization
        organization = Organization(id=organization_id)
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    def test_order_products_one_order(self):
        from ticketing.venues.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum
        from ticketing.products.models import Stock, StockStatus, Product, ProductItem

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(5)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.Vacant)) for i in range(2)]
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1)
        product = Product(id=1, price=100, items=[product_item])
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        [self.session.add(s) for s in seats]
        [self.session.add(s) for s in seat_statuses]

        # 座席隣接状態
        adjacency_set = SeatAdjacencySet(id=adjacency_set_id, seat_count=2)
        adjacency = SeatAdjacency(adjacency_set=adjacency_set, id=adjacency_id)
        for seat in seats:
            seat.adjacencies.append(adjacency)
        self.session.add(adjacency_set)
        self.session.add(adjacency)
        self.session.flush()


        # 注文 S席 2枚
        ordered_products = [(product, 2)]


        request = testing.DummyRequest()
        target = self._makeOne(request)
        #precondition
        result = list(target._convert_order_product_items(ordered_products))[0]
        self.assertEqual(result, (product_item, 2))
        result = list(target.quantity_for_stock_id(ordered_products))[0]
        self.assertEqual(result, (stock.id, 2))

        cart = target.order_products(ordered_products)


        self.assertIsNotNone(cart)
        self.assertEqual(len(cart.products), 1)
        self.assertEqual(len(cart.products[0].items), 1)
        self.assertEqual(cart.products[0].items[0].quantity, 2)

        from sqlalchemy import sql
        stock_statuses = self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock.id))
        for stock_status in stock_statuses:
            self.assertEqual(stock_status.quantity, 98)

class ReserveViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()
        self.config = testing.setUp()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()

    def _getTarget(self):
        from .views import ReserveView
        return ReserveView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_order_items_empty(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.ordered_items

        self.assertEqual(list(result), [])

    def test_order_items(self):
        from ticketing.products.models import Product
        p1 = Product(id=1, price=100)
        p2 = Product(id=2, price=150)
        self.session.add(p1)
        self.session.add(p2)
        params = {
            "product-1": '10',
            "a": 'aaa',
            "product-a": 'x',
            "product-2": '20',
            }
        request = testing.DummyRequest(params=params)
        target = self._makeOne(request)
        result = target.iter_ordered_items()

        self.assertEqual(list(result), [("1", 10), ("2", 20)])

    def test_ordered_items(self):
        from ticketing.products.models import Product
        p1 = Product(id=1, price=100)
        p2 = Product(id=2, price=150)
        self.session.add(p1)
        self.session.add(p2)
        params = {
            "product-1": '10',
            "a": 'aaa',
            "product-a": 'x',
            "product-2": '20',
            }
        request = testing.DummyRequest(params=params)
        target = self._makeOne(request)
        result = target.ordered_items

        self.assertEqual(list(result), [(p1, 10), (p2, 20)])


    def _add_venue(self, organization_id, site_id, venue_id):
        from ticketing.venues.models import Venue, Site
        from ticketing.organizations.models import Organization
        organization = Organization(id=organization_id)
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    def test_it(self):


        from ticketing.venues.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum
        from ticketing.products.models import Stock, StockStatus, Product, ProductItem
        from .models import Cart
        from .resources import TicketingCartResrouce

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(2)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.Vacant)) for i in range(2)]
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1)
        product = Product(id=1, price=100, items=[product_item])
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        [self.session.add(s) for s in seats]
        [self.session.add(s) for s in seat_statuses]

        # 座席隣接状態
        adjacency_set = SeatAdjacencySet(id=adjacency_set_id, seat_count=2)
        adjacency = SeatAdjacency(adjacency_set=adjacency_set, id=adjacency_id)
        for seat in seats:
            seat.adjacencies.append(adjacency)
        self.session.add(adjacency_set)
        self.session.add(adjacency)
        self.session.flush()


        params = {
            "product-" + str(product.id): '2',
            }

        request = testing.DummyRequest(params=params)
        request.context = TicketingCartResrouce(request)
        target = self._makeOne(request)
        result = target()

        import transaction
        transaction.commit()

        self.assertEqual(result, dict(result='OK'))
        cart_id = request.session['ticketing.cart_id']

        self.session.remove()
        cart = self.session.query(Cart).filter(Cart.id==cart_id).one()

        self.assertIsNotNone(cart)
        self.assertEqual(len(cart.products), 1)
        self.assertEqual(len(cart.products[0].items), 1)
        self.assertEqual(cart.products[0].items[0].quantity, 2)

        from sqlalchemy import sql
        stock_statuses = self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock_id))
        for stock_status in stock_statuses:
            self.assertEqual(stock_status.quantity, 98)

    def test_it_no_stock(self):

        from ticketing.venues.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum
        from ticketing.products.models import Stock, StockStatus, Product, ProductItem
        from .models import Cart
        from .resources import TicketingCartResrouce

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=0)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(5)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.InCart)) for i in range(5)]
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1)
        product = Product(id=1, price=100, items=[product_item])
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        [self.session.add(s) for s in seats]
        [self.session.add(s) for s in seat_statuses]

        # 座席隣接状態
        adjacency_set = SeatAdjacencySet(id=adjacency_set_id, seat_count=2)
        adjacency = SeatAdjacency(adjacency_set=adjacency_set, id=adjacency_id)
        for seat in seats:
            seat.adjacencies.append(adjacency)
        self.session.add(adjacency_set)
        self.session.add(adjacency)
        self.session.flush()


        params = {
            "product-" + str(product.id): '2',
            }

        request = testing.DummyRequest(params=params)
        request.context = TicketingCartResrouce(request)
        target = self._makeOne(request)
        result = target()

        self.assertEqual(result, dict(result='NG'))
        cart_id = request.session.get('ticketing.cart_id')
        self.assertIsNone(cart_id)

    def test_it_no_seat(self):


        from ticketing.venues.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum
        from ticketing.products.models import Stock, StockStatus, Product, ProductItem
        from .models import Cart
        from .resources import TicketingCartResrouce

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(2)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.InCart)) for i in range(2)]
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1)
        product = Product(id=1, price=100, items=[product_item])
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        [self.session.add(s) for s in seats]
        [self.session.add(s) for s in seat_statuses]

        # 座席隣接状態
        adjacency_set = SeatAdjacencySet(id=adjacency_set_id, seat_count=2)
        adjacency = SeatAdjacency(adjacency_set=adjacency_set, id=adjacency_id)
        for seat in seats:
            seat.adjacencies.append(adjacency)
        self.session.add(adjacency_set)
        self.session.add(adjacency)
        self.session.flush()


        params = {
            "product-" + str(product.id): '2',
            }

        request = testing.DummyRequest(params=params)
        request.context = TicketingCartResrouce(request)
        target = self._makeOne(request)
        result = target()

        self.assertEqual(result, dict(result='NG'))
        cart_id = request.session.get('ticketing.cart_id')
        self.assertIsNone(cart_id)
        from sqlalchemy import sql
        stock_statuses = self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock_id))
        for stock_status in stock_statuses:
            self.assertEqual(stock_status.quantity, 100)

class PyamentViewTests(unittest.TestCase):

    def _getTarget(self):
        from . import views
        return views.PaymentView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_it_no_cart(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target()
        self.assertEqual(result.location, '/')