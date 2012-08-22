import unittest

class CartedProductItemTests(unittest.TestCase):
    def setUp(self):
        import ticketing.core.models # for the depencency

    def _getTarget(self):
        from .models import CartedProductItem
        return CartedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_seats(self, num):
        from ticketing.core.models import Seat
        return [Seat(name=u"Seat %d" % i,
                     l0_id="seat-%d" % i) for i in range(num)]
            
    def test_seatdicts(self):
        target = self._makeOne(seats=self._create_seats(4))

        result = target.seatdicts

        self.assertEqual(list(result), 
            [{'l0_id': 'seat-0', 'name': u'Seat 0'},
             {'l0_id': 'seat-1', 'name': u'Seat 1'},
             {'l0_id': 'seat-2', 'name': u'Seat 2'},
             {'l0_id': 'seat-3', 'name': u'Seat 3'}])

class CartedProductTests(unittest.TestCase):
    
    def _getTarget(self):
        from .models import CartedProduct
        return CartedProduct

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_seats(self, num, prefix):
        from ticketing.core.models import Seat
        return [Seat(name=u"Seat %s-%d" % (prefix, i),
                     l0_id="seat-%s-%d" % (prefix, i)) for i in range(num)]

    def _create_items(self, num):
        from .models import CartedProductItem
        return [CartedProductItem(seats=self._create_seats(2, i))
                for i in range(num)]

    def test_seats(self):
        target = self._makeOne(items=self._create_items(2))
        result = target.seats
        self.assertEqual(result, 
            [{'l0_id': 'seat-0-0', 'name': u'Seat 0-0'},
             {'l0_id': 'seat-0-1', 'name': u'Seat 0-1'},
             {'l0_id': 'seat-1-0', 'name': u'Seat 1-0'},
             {'l0_id': 'seat-1-1', 'name': u'Seat 1-1'}])
