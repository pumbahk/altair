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
)
from altair.app.ticketing.orders.models import (
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

    def get_event_progress(self, event, product_item_id, start_on, end_on):
        assert event.organization_id == self.organization.id
        return EventPrintProgress(event, product_item_id, start_on, end_on)

    def get_event_progress_easy(self, event, product_item_id, start_on, end_on):
        return EventPrintProgress(event, product_item_id, start_on, end_on)

    def get_performance_progress(self, performance, product_item_id, start_on, end_on):
        assert performance.event.organization_id == self.organization.id
        return PerformancePrintProgress(performance, product_item_id, start_on, end_on)

    def get_performance_progress_easy(self, performance, product_item_id, start_on, end_on):
        return PerformancePrintProgress(performance, product_item_id, start_on, end_on)

class DummyPrintProgress(object):
    @reify
    def total(self):
        return 300

    @property
    def size(self):
        return 4

    @reify
    def qr(self):
        return ProgressData(total=100, printed=40, unprinted=60)

    @reify
    def shipping(self):
        return ProgressData(total=100, printed=100, unprinted=0)

    @reify
    def reserved(self):
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

    def filter_by_printed_token(self, query, start_on=None, end_on=None):
        if start_on and end_on:
            query = query.filter(OrderedProductItemToken.printed_at >= start_on)
            query = query.filter(OrderedProductItemToken.printed_at <= end_on)

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
        return 4

    @reify
    def qr(self):
        query = self.filtering.include_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            [ plugins.QR_DELIVERY_PLUGIN_ID, plugins.ORION_DELIVERY_PLUGIN_ID ]
        )
        total = query.count()
        all_printed = self.filtering.filter_by_printed_token(query).count()
        printed = self.filtering.filter_by_printed_token(query, self.start_on, self.end_on).count()
        return ProgressData(total=total, printed=printed, unprinted=total-all_printed)

    @reify
    def shipping(self):
        query = self.filtering.include_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            plugins.SHIPPING_DELIVERY_PLUGIN_ID
        )
        total = query.count()
        all_printed = self.filtering.filter_by_printed_token(query).count()
        printed = self.filtering.filter_by_printed_token(query, self.start_on, self.end_on).count()
        return ProgressData(total=total, printed=printed, unprinted=total-all_printed)

    @reify
    def reserved(self):
        query = self.filtering.include_by_delivery_plugin(
            self.ordered_product_item_token_query,
            [plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
             plugins.WEB_COUPON_DELIVERY_PLUGIN_ID]
        )
        total = query.count()
        all_printed = self.filtering.filter_by_printed_token(query).count()
        printed = self.filtering.filter_by_printed_token(query, self.start_on, self.end_on).count()
        return ProgressData(total=total, printed=printed, unprinted=total-all_printed)

    @reify
    def other(self):
        query = self.filtering.exclude_by_delivery_plugin(
            self.ordered_product_item_token_query, 
            [plugins.SHIPPING_DELIVERY_PLUGIN_ID, plugins.ORION_DELIVERY_PLUGIN_ID, plugins.QR_DELIVERY_PLUGIN_ID,
             plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID, plugins.WEB_COUPON_DELIVERY_PLUGIN_ID]
        )
        total = query.count()
        all_printed = self.filtering.filter_by_printed_token(query).count()
        printed = self.filtering.filter_by_printed_token(query, self.start_on, self.end_on).count()
        return ProgressData(total=total, printed=printed, unprinted=total-all_printed)


class PerformancePrintProgress(PrintProgressBase):
    def __init__(self, performance, product_item_id=None, start_on=None, end_on=None):
        self.performance = performance
        self.filtering = TokenQueryFilter()
        self.product_item_id = product_item_id
        self.start_on = start_on
        self.end_on = end_on

    @reify
    def performance_id_list(self):
        return [self.performance.id]

    @reify
    def ordered_product_item_token_query(self):
        query = (OrderedProductItemToken.query
                .join(OrderedProductItem)
                .join(OrderedProduct)
                .join(Order)
                .filter(Order.performance==self.performance)
                .filter(Order.canceled_at==None)
                .filter(Order.deleted_at==None))
        if self.product_item_id and self.product_item_id != u"None":
            query = query.filter(OrderedProductItem.product_item_id == self.product_item_id)
        return query

class EventPrintProgress(PrintProgressBase):
    def __init__(self, event, product_item_id=None, start_on=None, end_on=None):
        self.event = event
        self.filtering = TokenQueryFilter()
        self.product_item_id = product_item_id
        self.start_on = start_on
        self.end_on = end_on

    @reify
    def performance_id_list(self):
        return [p.id for p in self.event.performances]

    @reify
    def ordered_product_item_token_query(self):
        query = (OrderedProductItemToken.query
                .join(OrderedProductItem)
                .join(OrderedProduct)
                .join(Order)
                .filter(Order.performance_id.in_(self.performance_id_list))
                .filter(Order.canceled_at==None)
                .filter(Order.deleted_at==None))
        if self.product_item_id and self.product_item_id != u"None":
            query = query.filter(OrderedProductItem.product_item_id == self.product_item_id)
        return query
