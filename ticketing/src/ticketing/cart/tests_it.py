import unittest
from pyramid import testing
from .testing import _setup_db

def _setup_it(config):
    from pyramid.interfaces import IRequest
    from .interfaces import IStocker, IReserving, ICartFactory
    from .stocker import Stocker
    from .reserving import Reserving
    from .carting import CartFactory
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    config.add_route('cart.payment', 'cart/payment')

class ReserveViewTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()

    def setUp(self):
        self.config = testing.setUp()
        _setup_it(self.config)

    def _getTarget(self):
        from .views import ReserveView
        return ReserveView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_seats(self):
        import ticketing.core.models as c_m
        import ticketing.orders.models as o_m
        # organization
        org = c_m.Organization()
        # event
        event = c_m.Event(organization=org)
        # performance
        performance = c_m.Performance(event=event)
        # site
        site = c_m.Site()
        # venue
        venue = c_m.Venue(site=site, organization=org, performance=performance)
        stock_type = c_m.StockType(quantity_only=False)
        quantity_only_stock_type = c_m.StockType(quantity_only=True)
        stock1 = c_m.Stock(stock_type=stock_type)
        stock2 = c_m.Stock(stock_type=stock_type)
        stock3 = c_m.Stock(stock_type=quantity_only_stock_type)
        product1 = c_m.Product(price=100)
        product2 = c_m.Product(price=200)
        product3 = c_m.Product(price=300)
        product_item1 = c_m.ProductItem(price=100, product=product1, stock=stock1)
        product_item2 = c_m.ProductItem(price=200, product=product2, stock=stock2)
        product_item3 = c_m.ProductItem(price=300, product=product3, stock=stock3)
        seat1 = c_m.Seat(stock=stock1, venue=venue)
        seat2 = c_m.Seat(stock=stock2, venue=venue)
        seat3 = c_m.Seat(stock=stock1, venue=venue)
        seat4 = c_m.Seat(stock=stock2, venue=venue)
        seat5 = c_m.Seat(stock=stock2, venue=venue)

        seats = [ seat1, seat2, seat3, seat4, seat5 ]

        self.session.add(stock1)
        self.session.add(stock2)
        self.session.add(stock3)
        self.session.flush()

        return performance, product1, product2, product3, seats

    def test_it_quantity_only(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, seats = self._add_seats()

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product3.id, 1),
        ])

        request = testing.DummyRequest(params=params, 
            context=testing.DummyResource())
        target = self._makeOne(request)

        results = target.reserve()

        self.assertEqual(results['result'], 'OK')

    def test_it_reserving(self):
        pass
