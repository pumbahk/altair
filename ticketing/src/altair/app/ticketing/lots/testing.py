# -*- coding:utf-8 -*-

from pyramid import testing
from zope.interface import implementer
from altair.app.ticketing.cart.interfaces import IStocker
from datetime import datetime


class DummySession(dict):
    def persist(self):
        pass


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

    from altair.app.ticketing.core.models import Organization, Event, SalesSegment, Performance, PerformanceSetting, Venue, Site
    
    #event = Event(id=1111)
    organization = Organization(code="test", short_name="test")
    event_id = 1111
    venue = Venue(name="testing-venue", site=Site(), organization=organization)
    setting = PerformanceSetting(entry_limit=1)
    performance = Performance(event_id=event_id, id=123, venue=venue, start_on=datetime(2013, 1, 1, 0, 0, 0), setting=setting)
    session.add(performance)
    sales_segment = SalesSegment(id=12345)
    lot = _add_lot(session, event_id, sales_segment.id, 5, membergroups=membergroups, venue=venue)
    lot.event.organization = organization
    lot.limit_wishes = 3
    products = _create_products(session, product_data)
    for p in products:
        p.performance = performance
        session.merge(p)
    session.flush()
    return lot, products

def login(config, user):
    import pickle
    data = pickle.dumps(user)
    data = data.encode('base64')
    config.testing_securitypolicy(userid=data)

def _create_products(session, values):
    from altair.app.ticketing.core.models import Product
    products = []
    for value in values:
        p = Product(**value)
        session.add(p)
        products.append(p)
    session.flush()
    return products

def _add_lot(session, event_id, sales_segment_group_id, num_performances, membergroups=[], num_products=3, venue=None):
    from . import models as m
    from altair.app.ticketing.core.models import (
        Event, Performance, PerformanceSetting, SalesSegment, StockType,
        PaymentMethod, DeliveryMethod, PaymentDeliveryMethodPair,
        Product,
    )
    # event
    event = Event(id=event_id)

    # payment_delivery_method
    payment_method = PaymentMethod(fee=0)
    delivery_method = DeliveryMethod(fee=0)
    payment_delivery_method_pair = PaymentDeliveryMethodPair( 
        payment_method=payment_method, delivery_method=delivery_method,
        system_fee=0, transaction_fee=0, delivery_fee=0, discount=0)


    # sales_segment
    sales_segment = SalesSegment(id=sales_segment_group_id, 
                                 payment_delivery_method_pairs=[payment_delivery_method_pair],
                                 )
                                 #membergroups=membergroups)

    # performances
    performances = []
    products = []
    for i in range(num_performances):
        p = Performance(name=u"パフォーマンス {0}".format(i),
                        venue=venue, event=event)
        session.add(p)
        performances.append(p)
        setting = PerformanceSetting(performance=p, entry_limit=1)
        session.add(setting)

        for j in range(num_products):
            seat_stock_type = StockType()
            product = Product(sales_segment=sales_segment,
                              performance=p,
                              price=i * 100 + j * 10,
                              seat_stock_type=seat_stock_type)
            products.append(product)

    lot = m.Lot(event=event, sales_segment=sales_segment)

    session.add(lot)
    session.flush()
    return lot
    
class DummyAuthenticatedResource(testing.DummyResource):
    def __init__(self, *args, **kwargs):
        testing.DummyResource.__init__(self, *args, **kwargs)
        if 'user' not in kwargs:
            self.user = None
            
    def authenticated_user(self):
        return self.user
