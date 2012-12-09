# -*- coding:utf-8 -*-

from pyramid import testing
from zope.interface import implementer
from ticketing.cart.interfaces import IStocker

@implementer(IStocker)
class DummyStocker(object):
    def __init__(self, result):
        self.result = result

    def take_stock(self, performance_id, product_requires):
        return self.result

class DummyStockerFactory(object):
    def __init__(self, result):
        self.result = result

    def __call__(self, request):
        return DummyStocker(self.result)


def _add_lots(session, product_data, membergroups):

    from ticketing.core.models import Organization
    
    event = testing.DummyModel(id=1111)
    sales_segment = testing.DummyModel(id=12345)
    lot = _add_lot(session, event.id, sales_segment.id, 5, 3, membergroups=membergroups)
    lot.event.organization = Organization(code="test", short_name="test")
    lot.limit_wishes =3 
    products = _create_products(session, product_data)
    for p in products:
        session.add(p)
    session.flush()
    return lot, products

def login(config, user):
    import pickle
    data = pickle.dumps(user)
    data = data.encode('base64')
    config.testing_securitypolicy(userid=data)

def _create_products(session, values):
    from ticketing.core.models import Product
    products = []
    for value in values:
        p = Product(**value)
        session.add(p)
        products.append(p)
    session.flush()
    return products

def _add_lot(session, event_id, sales_segment_id, num_performances, num_stok_types, membergroups=[]):
    from . import models as m
    from ticketing.core.models import (
        Event, Performance, SalesSegment, StockType,
        PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair,
    )
    # event
    event = Event(id=event_id)
    # performances
    performances = []
    for i in range(num_performances):
        p = Performance(name=u"パフォーマンス {0}".format(i))
        session.add(p)
        performances.append(p)

    # stock_types
    stock_types = []
    for i in range(num_stok_types):
        s = StockType(name=u"席 {0}".format(i))
        session.add(s)
        stock_types.append(s)
    # sales_segment
    sales_segment = SalesSegment(id=sales_segment_id, event=event, membergroups=membergroups)
    # payment_delivery_method
    payment_method = PaymentMethod(fee=0)
    delivery_method = DeliveryMethod(fee=0)
    payment_delivery_method_pair = PaymentDeliveryMethodPair(sales_segment=sales_segment, 
        payment_method=payment_method, delivery_method=delivery_method,
        system_fee=0, transaction_fee=0, delivery_fee=0, discount=0)

    lot = m.Lot(event=event, sales_segment=sales_segment, performances=performances, stock_types=stock_types)
    session.add(lot)
    session.flush()
    return lot
