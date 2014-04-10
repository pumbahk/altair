# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sqlalchemy as sa
from pyramid.decorator import reify
from altair.app.ticketing.core.models import (
    Event,
    Performance, 
    PaymentDeliveryMethodPair,
    DeliveryMethod, 
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
)
from altair.app.ticketing.payments import plugins

from collections import namedtuple
ProgressData = namedtuple("ProgressData", "total printed unprinted")


"""
そもそもprinted_at以外みない
"""

class PrintProgressGetter(object):
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    def get_event_progress(self, event):
        assert event.organization_id == self.organization.id
        return EventPrintProgress(event)

    def get_performance_progress(self, performance):
        assert performance.event.organization_id == self.organization.id
        return PerformancePrintProgress(performance)

class DummyPrintProgress(object):
    @reify
    def total(self):
        return 300

    @property
    def size(self):
        return 3

    @reify
    def qr(self):
        return ProgressData(total=100, printed=40, unprinted=60)

    @reify
    def shipping(self):
        return ProgressData(total=100, printed=100, unprinted=0)

    @reify
    def other(self):
        return ProgressData(total=20, printed=19, unprinted=1)

class TokenQueryFilter(object):
    #query = ordered_product_item_token_query
    def include_by_delivery_plugin(self, query, delivery_plugin_id):
        if isinstance(delivery_plugin_id, (list, tuple)):
            cond = DeliveryMethod.delivery_plugin_id.in_(delivery_plugin_id)
        else:
            cond = DeliveryMethod.delivery_plugin_id==delivery_plugin_id
        return query.filter(
            Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id, 
            PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id, 
            cond
        )

    def exclude_by_delivery_plugin(self, query, delivery_plugin_id):
        if isinstance(delivery_plugin_id, (list, tuple)):
            cond = sa.not_(DeliveryMethod.delivery_plugin_id.in_(delivery_plugin_id))
        else:
            cond = DeliveryMethod.delivery_plugin_id!=delivery_plugin_id
        return query.filter(
            Order.payment_delivery_method_pair_id==PaymentDeliveryMethodPair.id, 
            PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id, 
            cond
        )

    def filter_by_printed_token(self, query):
        return query.filter(
            sa.and_(OrderedProductItemToken.printed_at != None, 
                    sa.or_(OrderedProductItemToken.refreshed_at == None, 
                           OrderedProductItemToken.printed_at > OrderedProductItemToken.refreshed_at)
                )
        )

class PrintProgressBase(object):
    filtering = None
    ordered_product_item_token_query = None

    @reify
    def total(self):
        return self.ordered_product_item_token_query.count()

    @property
    def size(self):
        return 3

    @reify
    def qr(self):
        query = self.filtering.include_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            [ plugins.QR_DELIVERY_PLUGIN_ID, plugins.ORION_DELIVERY_PLUGIN_ID ]
        )
        total = query.count()
        printed = self.filtering.filter_by_printed_token(query).count()
        return ProgressData(total=total, printed=printed, unprinted=total-printed)

    @reify
    def shipping(self):
        query = self.filtering.include_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )
        total = query.count()
        printed = self.filtering.filter_by_printed_token(query).count()
        return ProgressData(total=total, printed=printed, unprinted=total-printed)

    @reify
    def other(self):
        query = self.filtering.exclude_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            [plugins.SHIPPING_DELIVERY_PLUGIN_ID, plugins.ORION_DELIVERY_PLUGIN_ID,  plugins.QR_DELIVERY_PLUGIN_ID]
        )
        total = query.count()
        printed = self.filtering.filter_by_printed_token(query).count()
        return ProgressData(total=total, printed=printed, unprinted=total-printed)


class PerformancePrintProgress(PrintProgressBase):
    def __init__(self, performance):
        self.performance = performance
        self.filtering = TokenQueryFilter()

    @reify
    def ordered_product_item_token_query(self):
        return (OrderedProductItemToken.query
                .join(OrderedProductItem)
                .join(OrderedProduct)
                .join(Order)
                .filter(Order.performance==self.performance)
                .filter(Order.canceled_at==None)
                .filter(Order.deleted_at==None))

class EventPrintProgress(PrintProgressBase):
    def __init__(self, event):
        self.event = event
        self.filtering = TokenQueryFilter()

    @reify
    def performance_id_list(self):
        return [p.id for p in self.event.performances]

    @reify
    def ordered_product_item_token_query(self):
        return (OrderedProductItemToken.query
                .join(OrderedProductItem)
                .join(OrderedProduct)
                .join(Order)
                .filter(Order.performance_id.in_(self.performance_id_list))
                .filter(Order.canceled_at==None)
                .filter(Order.deleted_at==None))
