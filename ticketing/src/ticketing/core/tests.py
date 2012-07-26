# -*- coding:utf-8 -*-

# move it.
import unittest

def get_organization(*args, **kwargs):
    from .models import Organization
    return Organization(*args, **kwargs)

class EventCMSDataTests(unittest.TestCase):
    def _getTarget(self):
        from .models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_data_include_organazation_id(self):
        organization = get_organization(id=10000)
        target = self._makeOne(organization=organization)
        result = target._get_self_cms_data()
        self.assertEqual(result["organization_id"], 10000)

class ProductTests(unittest.TestCase):
    def setUp(self):

        # あとで ticketing.testingの_setup_db呼ぶように変更する
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///")
        import sqlahelper
        sqlahelper.add_engine(engine)
        from ticketing.core import models
        models.Base.metadata.create_all()
        self.session = sqlahelper.get_session()

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _getTarget(self):
        from .models import Product
        return Product

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_performance(self):
        from .models import Performance
        return Performance()

    def _create_stock(self):
        from .models import Stock, StockType
        stock_type = StockType()
        return Stock(stock_type=stock_type)
        
    def _create_items(self, performance, stock, quantities):
        from .models import ProductItem
        return [ProductItem(price=0, performance=performance, stock=stock, quantity=q) for q in quantities]

    def test_get_quantity_power(self):
        performance = self._create_performance()
        stock1 = self._create_stock()
        stock2 = self._create_stock()
        target = self._makeOne(
            price=0,
            items=self._create_items(performance, stock1, [1, 2]) + self._create_items(performance, stock2, [3, 4]))

        self.session.add(performance)
        self.session.flush()
        result = target.get_quantity_power(stock1.stock_type, performance.id)

        self.assertEqual(result, 3)
        

if __name__ == "__main__":
    unittest.main()

