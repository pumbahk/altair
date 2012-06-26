# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from .testing import DummyRequest, DummySecure3D
import mock

def _setup_db():
    import sqlahelper
    from sqlalchemy import create_engine
    from . import models
    import ticketing.models
    import ticketing.orders.models
    import ticketing.users.models
    import ticketing.multicheckout.models

    engine = create_engine("sqlite:///")
    sqlahelper.get_session().remove()
    sqlahelper.add_engine(engine)
    sqlahelper.get_base().metadata.drop_all()
    sqlahelper.get_base().metadata.create_all()
    return sqlahelper.get_session()

def _teardown_db():
    import transaction
    transaction.abort()

class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('ticketing.cart')
        self.session = _setup_db()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _set_payment_url(self):
        from . import helpers as h
        self.config.add_route('test.payment', 'payment/3d')
        request = testing.DummyRequest()
        payment_method_manager = h.get_payment_method_manager(request)
        payment_method_manager.add_route_name('3', 'test.payment')

    def test_payment_method_url_multicheckout(self):
        from . import helpers as h
        self._set_payment_url()
        request = DummyRequest()
        result = h.get_payment_method_url(request, "3")

        self.assertEqual(result, "http://example.com/payment/3d")

    def test_get_or_create_user_create(self):
        from . import helpers as h
        request = DummyRequest()
        result = h.get_or_create_user(request, 'http://example.com/clamed_id')
        self.assertIsNone(result.id)
        self.assertEqual(result.user_credential[0].auth_identifier, 'http://example.com/clamed_id')
        self.assertEqual(result.user_credential[0].membership.name, 'rakuten')

    def _add_user(self, clamed_id):
        from ..users.models import User, UserCredential, MemberShip
        user = User()
        membership = MemberShip(name="rakuten")
        credential = UserCredential(user=user, auth_identifier=clamed_id, membership=membership)
        self.session.add(user)
        self.session.flush()
        return user

    def test_get_or_create_user_get(self):
        from . import helpers as h
        
        user = self._add_user('http://example.com/clamed_id')
        request = DummyRequest()
        result = h.get_or_create_user(request, 'http://example.com/clamed_id')
        self.assertEqual(result.id, user.id)
        self.assertEqual(result.user_credential[0].auth_identifier, 'http://example.com/clamed_id')
        self.assertEqual(result.user_credential[0].membership.name, 'rakuten')

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
        target = self._makeOne(system_fee=0, 
            payment_delivery_pair=testing.DummyModel(
                transaction_fee=0,
                delivery_fee=0,
                payment_method=testing.DummyModel(fee_type=0),
                delivery_method=testing.DummyModel(fee_type=0),
            ))
        self.assertEqual(target.total_amount, 0)

    def test_total_amount(self):
        from . import models
        target = self._makeOne(system_fee=0, 
            payment_delivery_pair=testing.DummyModel(
                transaction_fee=0,
                delivery_fee=0,
                payment_method=testing.DummyModel(fee_type=0),
                delivery_method=testing.DummyModel(fee_type=0),
            ))
        target.products = [
            models.CartedProduct(quantity=10, product=testing.DummyModel(price=10)),
            models.CartedProduct(quantity=10, product=testing.DummyModel(price=20)),
            ]
        self.assertEqual(target.total_amount, 300)

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
            testing.DummyResource(stock_id=1, performance_id=1),
        ]), 1) for i in range(10)]
        seats = [testing.DummyResource(id=i, stock_id=1) for i in range(10)]
        target = self._makeOne(performance_id=1)
        target.add_seat(seats, ordered_products)

        self.assertEqual(target.products[0].product.id, 0)
        self.assertEqual(target.products[0].quantity, 1)
        self.assertEqual(len(target.products[0].items), 1)

    def test_add_products(self):
        ordered_products = [(testing.DummyResource(id=i, items=[
            testing.DummyResource(stock_id=1, performance_id=1),
            ]), 1) for i in range(10)]
        target = self._makeOne(performance_id=1)
        target.add_products(ordered_products)

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
        product = testing.DummyResource(items=[testing.DummyResource(stock_id=2, performance_id=1),
                                               testing.DummyResource(stock_id=3, performance_id=1)])
        target = self._makeOne(id=1, product=product, quantity=1)
        result = target.pop_seats([testing.DummyResource(stock_id=1),
                                   testing.DummyResource(stock_id=2),
                                   testing.DummyResource(stock_id=3)],
            performance_id=1)

        self.assertEqual(len(target.items), 2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].stock_id, 1)

    def test_amount(self):
        product = testing.DummyResource(price=150)
        target = self._makeOne(id=1, product=product, quantity=3)

        self.assertEqual(target.amount, 450)

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

    def _add_seat(self, carted_product_item, quantity):
        from ..core import models as c_models

        seat_statuses = []
        organization = c_models.Organization(id=532)
        site = c_models.Site(id=899)
        venue = c_models.Venue(id=100, site=site, organization=organization)
        for i in range(quantity):
            seat = c_models.Seat(id=i, venue=venue)
            status = c_models.SeatStatus(seat=seat, status=int(c_models.SeatStatusEnum.InCart))
            carted_product_item.seats.append(seat)
            seat_statuses.append(status)
            self.session.add(seat)
        return seat_statuses

    def test_finish(self):
        target = self._makeOne(id=1)
        statuses = self._add_seat(target, 10)
        target.finish()

        self._assertAllOrdered(statuses)

    def _assertAllOrdered(self, statuses):
        from ..core.models import SeatStatusEnum
        for s in statuses:
            self.assertEqual(s.status, int(SeatStatusEnum.Ordered))


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

    def _add_event(self, event_id):
        from ..core import models
        event = models.Event(id=event_id)
        self.session.add(event)

    def _add_sales_segement(self, event_id, start_at, end_at):
        from ..core import models
        sales_segment = models.SalesSegment(
            event_id=event_id,
            start_at=start_at,
            end_at=end_at,
        )
        self.session.add(sales_segment)
        return sales_segment

    def test_event_id(self):
        request = DummyRequest(matchdict={"event_id": "this-is-event"})
        target = self._makeOne(request)

        result = target.event_id

        self.assertEqual(result, "this-is-event")

    @mock.patch("ticketing.cart.resources.datetime")
    def test_get_sales_segment(self, mock_datetime):
        from datetime import datetime
        mock_datetime.now.return_value = datetime(2012, 6, 20)

        event_id = "99"
        ss1 = self._add_sales_segement(event_id=event_id, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 30))
        ss2 = self._add_sales_segement(event_id=event_id, start_at=datetime(2012, 6, 21), end_at=datetime(2012, 6, 30))
        ss3 = self._add_sales_segement(event_id=event_id, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 19))
        self.session.flush()

        request = DummyRequest(matchdict={'event_id': event_id})
        target = self._makeOne(request)
        result = target.get_sales_segument()

        self.assertIsNotNone(result)
        self.assertEqual(result.id, ss1.id)

    # TODO: ダミーからモデルクラスに変更
#    def test_convert_order_product_items(self):
#        request = testing.DummyRequest()
#        target = self._makeOne(request)
#
#        performance_id = 1
#
#        products = [(testing.DummyResource(items=[testing.DummyResource() for j in range(2)]), i) for i in range(5)]
#        result = list(target._convert_order_product_items(performance_id, products))
#
#        self.assertEqual(len(result), 10)
#        self.assertEqual(result[0][1], 0)
#        self.assertEqual(result[5][1], 2)
#        self.assertEqual(result[9][1], 4)

    # TODO: ダミーからモデルクラスに変更
#    def test_quantity_for_stock_id(self):
#        import random
#
#        performance_id = 1
#
#        ordered_products = [
#            # 大人 S席
#            (testing.DummyResource(items=[testing.DummyResource(stock_id=1)]), 2),
#            # 子供 S席
#            (testing.DummyResource(items=[testing.DummyResource(stock_id=1)]), 3),
#            # 大人 S席 + 駐車場
#            (testing.DummyResource(items=[testing.DummyResource(stock_id=1),
#                                          testing.DummyResource(stock_id=2)]), 1),
#            ]
#
#        random.shuffle(ordered_products)
#        request = testing.DummyRequest()
#        target = self._makeOne(request)
#
#        result = list(target.quantity_for_stock_id(performance_id, ordered_products))
#
#        self.assertEqual(len(result), 2)
#        self.assertEqual(result[0], (1, 6))
#        self.assertEqual(result[1], (2, 1))

#    def test_order_products_empty(self):
#        request = testing.DummyRequest()
#
#        target = self._makeOne(request)
#        performance_id = 1
#
#        ordered_products = []
#        cart = target.order_products(performance_id, ordered_products)
#
#        self.assertIsNotNone(cart)
#        self.assertEqual(len(cart.products), 0)

    def _add_venue(self, organization_id, site_id, venue_id):
        from ticketing.core.models import Venue, Site
        from ..core.models import Organization
        organization = Organization(id=organization_id)
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    def test_order_products_one_order(self):
        from ..core. models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum, Stock, StockStatus, Product, ProductItem, Performance

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7
        performance_id = 8

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(5)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.Vacant)) for i in range(2)]
        performance = Performance(id=performance_id)
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
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
#        result = list(target._convert_order_product_items(ordered_products))[0]
#        self.assertEqual(result, (product_item, 2))
#        result = list(target.quantity_for_stock_id(ordered_products))[0]
#        self.assertEqual(result, (stock.id, 2))

        cart = target.order_products(performance_id, ordered_products)


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
        from ticketing.core.models import Product
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
        from ticketing.core.models import Product
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
        from ticketing.core.models import Venue, Site
        from ..core.models import Organization
        organization = Organization(id=organization_id)
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    def test_it(self):


        from ticketing.core.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum, Stock, StockStatus, Product, ProductItem, Performance
        from .models import Cart
        from .resources import TicketingCartResrouce

        self.config.add_route('cart.payment', 'payment')
        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7
        performance_id = 8

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(2)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.Vacant)) for i in range(2)]
        performance = Performance(id=performance_id)
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
        product = Product(id=1, price=100, items=[product_item], name=u"S席")
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
            "performance_id": performance.id,
            "product-" + str(product.id): '2',
            }

        request = testing.DummyRequest(params=params)
        request.context = TicketingCartResrouce(request)
        target = self._makeOne(request)
        result = target()

        import transaction
        transaction.commit()

        self.assertEqual(result, {'cart': {'products': [{'name': u'S席', 
                                                         'price': 100, 
                                                         'quantity': 2}],
                                           'total_amount': '200'},
                                  'result': 'OK', 
                                  'payment_url': 'http://example.com/payment'} )
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

        from ticketing.core.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum, Stock, StockStatus, Product, ProductItem, Performance
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
        performance_id = 8

        venue = self._add_venue(organization_id, site_id, venue_id)
        stock = Stock(id=stock_id, quantity=100)
        stock_status = StockStatus(stock_id=stock.id, quantity=0)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(5)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.InCart)) for i in range(5)]
        performance = Performance(id=performance_id)
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
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
            "performance_id": performance.id,
            "product-" + str(product.id): '2',
            }

        request = testing.DummyRequest(params=params)
        request.context = TicketingCartResrouce(request)
        target = self._makeOne(request)
        result = target()

        self.assertEqual(result, dict(result='NG'))
        cart_id = request.session.get('ticketing.cart_id')
        self.assertIsNone(cart_id)

    # 数受け処理にふっているため、このテストは通らない
#    def test_it_no_seat(self):
#
#
#        from ticketing.core.models import Seat, SeatAdjacency, SeatAdjacencySet, SeatStatus, SeatStatusEnum, Stock, StockStatus, Product, ProductItem, Performance
#        from .models import Cart
#        from .resources import TicketingCartResrouce
#
#        # 在庫
#        stock_id = 1
#        product_item_id = 2
#        adjacency_set_id = 3
#        adjacency_id = 4
#        venue_id = 5
#        site_id = 6
#        organization_id = 7
#        performance_id = 8
#
#        venue = self._add_venue(organization_id, site_id, venue_id)
#        stock = Stock(id=stock_id, quantity=100)
#        stock_status = StockStatus(stock_id=stock.id, quantity=100)
#        seats = [Seat(id=i, stock_id=stock.id, venue=venue) for i in range(2)]
#        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.InCart)) for i in range(2)]
#        performance = Performance(id=performance_id)
#        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
#        product = Product(id=1, price=100, items=[product_item])
#        self.session.add(stock)
#        self.session.add(product)
#        self.session.add(product_item)
#        self.session.add(stock_status)
#        [self.session.add(s) for s in seats]
#        [self.session.add(s) for s in seat_statuses]
#
#        # 座席隣接状態
#        adjacency_set = SeatAdjacencySet(id=adjacency_set_id, seat_count=2)
#        adjacency = SeatAdjacency(adjacency_set=adjacency_set, id=adjacency_id)
#        for seat in seats:
#            seat.adjacencies.append(adjacency)
#        self.session.add(adjacency_set)
#        self.session.add(adjacency)
#        self.session.flush()
#
#
#        params = {
#            "performance_id": performance.id,
#            "product-" + str(product.id): '2',
#            }
#
#        request = testing.DummyRequest(params=params)
#        request.context = TicketingCartResrouce(request)
#        target = self._makeOne(request)
#        result = target()
#
#        self.assertEqual(result, dict(result='NG'))
#        cart_id = request.session.get('ticketing.cart_id')
#        self.assertIsNone(cart_id)
#        from sqlalchemy import sql
#        stock_statuses = self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock_id))
#        for stock_status in stock_statuses:
#            self.assertEqual(stock_status.quantity, 100)

    def test_iter_ordered_items(self):
        params = [
            ("product-10", '2'),
            ("product-11", '0'),
            ("product-12", '10'),
            ]

        class DummyParams(object):
            def __init__(self, params):
                self.params = params
            def iteritems(self):
                for k, v in self.params:
                    yield k, v

        request = testing.DummyRequest(params=DummyParams(params))
        target = self._makeOne(request)
        result = list(target.iter_ordered_items())

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ('10', 2))
        self.assertEqual(result[1], ('12', 10))


class PaymentViewTests(unittest.TestCase):

    def _getTarget(self):
        from . import views
        return views.PaymentView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _register_starndard_payment_methods(self):
        from ..core import models
        self.session.add(models.PaymentMethod(id=1, name=u"セブンイレブン", fee=100))
        self.session.add(models.PaymentMethod(id=2, name=u"楽天あんしん決済", fee=100))
        self.session.add(models.PaymentMethod(id=3, name=u"クレジットカード", fee=100))
        self.config.add_route('route.1', 'sej')
        self.config.add_route('route.2', 'checkout')
        self.config.add_route('route.3', 'multi')
        from . import interfaces
        class DummyMethodManager(object):
            def get_route_name(self, id):
                return 'route.%s' % id
        dummy_method_manager = DummyMethodManager()
        self.config.registry.utilities.register([], interfaces.IPaymentMethodManager, "", dummy_method_manager)

    def test_it_no_cart(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target()
        self.assertEqual(result.location, '/')

    @mock.patch('ticketing.cart.helpers.get_or_create_user')
    @mock.patch('ticketing.cart.rakuten_auth.api.authenticated_user')
    def test_it(self, mock_authenticated_user, mock_get_ore_create_user):
        mock_authenticated_user.return_value = {
            'clamed_id': 'http://ticketstar.example.com/user/1'
        }
        mock_get_ore_create_user.return_value = testing.DummyModel(
            user_profile=testing.DummyModel(
                last_name=u'楽天',
                last_name_kana=u'ラクテン',
                first_name=u'太郎',
                first_name_kana=u'タロウ',
                tel_1="123456789",
                fax=None,
                zip=u"000-0000",
                prefecture=u"東京都",
                city=u"渋谷区",
                street=u"住所",
                address=u"",
                email='mail-address@example.com',
            ),
        )
        self._register_starndard_payment_methods()
        request = testing.DummyRequest()
        request._cart = testing.DummyModel(
            performance=testing.DummyModel(
                event=testing.DummyModel(
                    id="this-is-event-id",
                ),
            ),
        )
        request.context = testing.DummyResource()
        request.context.get_payment_delivery_method_pair = lambda: None
        target = self._makeOne(request)
        result = target()

        user = result['user']
        user_profile = result['user_profile']
        self.assertEqual(user_profile.last_name, u'楽天')

        # self.assertEqual(result,
        #         {'payments': [
        #             {'name': u'セブンイレブン',
        #              'url': 'http://example.com/sej'},
        #             {'name': u'楽天あんしん決済',
        #              'url': 'http://example.com/checkout'},
        #             {'name': u'クレジットカード',
        #              'url': 'http://example.com/multi'}]}
        # )


class PaymentContext(testing.DummyResource):
    pass

class DummyViewFactory(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def __call__(self, request):
        request.response.text = self.response_text
        return request.response

class FormRendererTests(unittest.TestCase):

    def _getTarget(self):
        from formrenderer import FormRenderer
        return FormRenderer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_errors(self):
        from wtforms.form import Form
        from wtforms.fields import TextField
        from wtforms.validators import Required
        from webob.multidict import MultiDict

        class DummyForm(Form):
            req_text = TextField(validators=[Required()])

        data = MultiDict()
        f = DummyForm(data)
        f.validate()

        target = self._makeOne(f)
        result = target.errors("req_text")

        self.assertEqual(result, "<ul>\n<li>This field is required.</li>\n</ul>")
