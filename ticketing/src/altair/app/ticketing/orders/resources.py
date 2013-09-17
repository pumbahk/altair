# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from sqlalchemy import or_ 
from sqlalchemy.orm import joinedload
from pyramid.decorator import reify

# from paste.util.multidict import MultiDict
from webob.multidict import MultiDict
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.models import (
    DBSession,
    record_to_multidict,
    )

from altair.app.ticketing.core.models import (
    Order, 
    OrderedProduct,
    OrderedProductItem,
    ProductItem,
    Product,
    Seat,
    TicketBundle, 
    OrderedProductItemToken
    )
from altair.app.ticketing.mailmags.models import(
    MailSubscription,
    MailMagazine,
    MailSubscriptionStatus
    )
from altair.app.ticketing.orders.forms import (
    OrderForm,
    OrderReserveForm,
    OrderRefundForm,
    OrderAttributesEditFormFactory, 
    ClientOptionalForm,
 )
from .enqueue import (
    get_enqueue_each_print_action, 
    JoinedObjectsForProductItemDependentsProvider
)
from altair.metadata.api import with_provided_values_iterator

class OrderDependentsProvilder(object):
    def __init__(self, order):
        self.order = order

    @property
    def histories(self):
        order = self.order
        return DBSession.query(Order, include_deleted=True)\
            .filter(Order.order_no==order.order_no)\
            .options(joinedload('ordered_products'), joinedload('ordered_products.ordered_product_items'))\
            .order_by(Order.branch_no.desc()).all()

    def get_order_attributes(self, metadata_provider_registry):
        itr = self.order.attributes.items()
        return with_provided_values_iterator(metadata_provider_registry, itr)


    @property
    def mail_magazines(self):
        order = self.order
        if order.shipping_address:
            mail_magazines = MailMagazine.query \
                .filter(MailMagazine.organization_id == order.organization_id) \
                .filter(MailSubscription.email == order.shipping_address.email_1) \
                .filter(or_(MailSubscription.status == None,
                            MailSubscription.status == MailSubscriptionStatus.Subscribed.v)) \
                            .distinct().all()
        else:
            mail_magazines = []
        if order.user and order.user.mail_subscription:
            mail_magazines += [ms.segment for ms in order.user.mail_subscription if ms.segment.organization_id == order.organization_id]
        return mail_magazines

    def describe_objects_for_product_item_provider(self): #todo:rename
        order_id = self.order.id
        qs = OrderedProduct.query.filter(OrderedProduct.order_id==order_id)
        qs = qs.join(OrderedProductItem).join(ProductItem, OrderedProductItem.product_item_id==ProductItem.id)
        qs = qs.outerjoin(OrderedProductItemToken, OrderedProductItem.id==OrderedProductItemToken.ordered_product_item_id)
        qs = qs.outerjoin(TicketBundle, ProductItem.ticket_bundle_id==TicketBundle.id)
        qs = qs.outerjoin(Seat, OrderedProductItemToken.seat_id==Seat.id)
        qs = qs.with_entities(OrderedProduct, OrderedProductItem, ProductItem, TicketBundle, Seat, OrderedProductItemToken.id)
        qs = qs.options(joinedload(ProductItem.product, Product.sales_segment))
        objs = qs.all()
        return JoinedObjectsForProductItemDependentsProvider(objs)


class OrderShowFormProvider(object):
    def __init__(self, order):
        self.order = order

    def get_shipping_address_form(self):
        order = self.order
        if order.shipping_address:
            form_shipping_address = ClientOptionalForm(record_to_multidict(order.shipping_address))
            form_shipping_address.tel_1.data = order.shipping_address.tel_1
            form_shipping_address.email_1.data = order.shipping_address.email_1
            form_shipping_address.email_2.data = order.shipping_address.email_2
        else:
            form_shipping_address = ClientOptionalForm()
        return form_shipping_address

    def get_order_form(self):
        order = self.order        
        return OrderForm(record_to_multidict(order))

    def get_order_reserve_form(self):
        order = self.order        
        return  OrderReserveForm(performance_id=order.performance_id)

    def get_order_refund_form(self):
        order = self.order        
        return OrderRefundForm(MultiDict(payment_method_id=order.payment_delivery_pair.payment_method.id), organization_id=order.organization_id)

    def get_order_edit_attribute(self):
        return OrderAttributesEditFormFactory(3)()

class OrderResource(TicketingAdminResource):
    @reify
    def order_id(self):
        return int(self.request.matchdict.get('order_id', 0))
    
    @reify
    def order(self):
        order = Order.get(self.order_id, self.organization.id, include_deleted=True)
        if order and order.deleted_at: #obsolete?
            return Order.filter_by(order_no=order.order_no).first()
        return order

class OrderPrintByTokenActionProvider(object):
    def __init__(self, order):
        self.order = order

    def get_print_candidate_action(self, candidate_id_list):
        #token@seat@ordered_product_item.id@ticket.id
        candidate_id_list = [[(None if e == "None" else unicode(e)) for e in xs.split("@")] for xs in candidate_id_list]
        return get_enqueue_each_print_action(self.order, candidate_id_list)


class OrderPrintEachResource(OrderResource):
    def get_dependents_actions(self, order):
        return OrderPrintByTokenActionProvider(order)

class OrdersShowResource(OrderResource):
    def get_dependents_models(self, order):
        return OrderDependentsProvilder(order)

    def get_dependents_forms(self, order):
        return OrderShowFormProvider(order)
