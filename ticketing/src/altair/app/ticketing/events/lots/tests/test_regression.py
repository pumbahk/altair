# -*- coding:utf-8 -*-
import unittest
import sqlahelper
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from altair.app.ticketing.core.testing import CoreTestMixin
from zope.interface import provider, implementer, directlyProvides
from altair.mq.interfaces import IPublisherConsumerFactory, IPublisher, IConsumer

@implementer(IPublisher, IConsumer)
@provider(IPublisherConsumerFactory)
class DummyPublisherConsumer(object):
    def __init__(self, config, config_prefix):
        pass

    def add_task(self, *args, **kwargs):
        pass

    def modify_task_dispatcher(self, dispatcher):
        return dispatcher


class LotAdminRegressionTest(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        from altair.app.ticketing import install_ld
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db([
            "altair.multicheckout",
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.cart.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.events.lots.models",
            "altair.app.ticketing.operators.models",
            ], hook=install_ld)
        self.request = DummyRequest()
        self.config = testing.setUp(
            request=self.request,
            autocommit=False,
            settings={
                'altair.ticketing.lots.mq': __name__ + '.DummyPublisherConsumer',
                }
            )
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        import altair.multicheckout.models
        altair.multicheckout.models.Base.metadata.create_all()
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.operators.models import Operator
        from altair.app.ticketing.core.models import Venue, Site
        self.operator = Operator(organization=self.organization)
        self.performance.venue = Venue(organization_id=self.organization.id, site=Site())
        self.config.include('altair.app.ticketing.lots.workers.includeme')
        self.config.include('altair.app.ticketing.events.lots')
        self.config.commit()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()
        import altair.multicheckout.models
        altair.multicheckout.models.Base.metadata.drop_all()

    def _getTarget(self):
        from ..views import LotEntries
        return LotEntries

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_search_entries(self):
        from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, Product, ProductItem, Stock, StockType, ShippingAddress, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
        from altair.app.ticketing.lots.models import Lot, LotEntry, LotEntryWish, LotEntryProduct
        sales_segment = SalesSegment(
            sales_segment_group=SalesSegmentGroup(event=self.event),
            )
        lot = Lot(
            event=self.event,
            sales_segment=sales_segment,
            limit_wishes=10
            )
        products = [
            Product(
                performance=self.performance,
                sales_segment=sales_segment,
                price=1000,
                items=[
                    ProductItem(
                        quantity=1,
                        price=1000,
                        stock=Stock(
                            stock_type=StockType(event=self.event, quantity_only=True),
                            performance=self.performance
                            )
                        )
                    ]
                )
            for i in range(5)
            ]
        for i in range(0, 100):
            lot_entry = LotEntry(
                lot=lot,
                payment_delivery_method_pair=PaymentDeliveryMethodPair(
                    system_fee=0,
                    transaction_fee=0,
                    discount=0,
                    payment_method=PaymentMethod(fee=0),
                    delivery_method=DeliveryMethod()
                    ),
                shipping_address=ShippingAddress(),
                wishes=[
                    LotEntryWish(
                        wish_order=j,
                        products=[
                            LotEntryProduct(
                                product=product,
                                quantity=1
                                )
                            ],
                        performance=product.performance
                        )
                    for j, product in enumerate(products)
                    ]
                )
            self.session.add(lot_entry)
        self.session.flush() 

        from ..views import LotEntries
        context = testing.DummyResource(
            user=self.operator,
            event=self.event,
            lot=lot,
            lot_id=lot.id
            )
        self.request.context = context
        target = LotEntries(context, self.request)
        self.request.params['do_search'] = 'do_search'
        self.request.params['wish_order'] = ""
        self.request.params['entried'] = 'y'
        self.request.params['electing'] = 'y'
        self.request.params['elected'] = 'y'
        self.request.params['rejecting'] = 'y'
        self.request.params['rejected'] = 'y'
        result = target.search_entries()
        self.assertEqual(500, result['wishes'].item_count)
