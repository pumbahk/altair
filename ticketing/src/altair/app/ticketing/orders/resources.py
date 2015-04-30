# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from sqlalchemy.sql.expression import or_, desc
from sqlalchemy.orm import joinedload, undefer, aliased
from pyramid.decorator import reify

# from paste.util.multidict import MultiDict
from webob.multidict import MultiDict
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.models import (
    DBSession,
    record_to_multidict,
    )

from altair.app.ticketing.core.models import (
    ProductItem,
    Product,
    Seat,
    Ticket,
    Ticket_TicketBundle,
    TicketFormat_DeliveryMethod,
    TicketBundle,
    TicketFormat,
    )
from altair.app.ticketing.orders.models import (
    Order, 
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    )
from altair.app.ticketing.mailmags.models import(
    MailSubscription,
    MailMagazine,
    MailSubscriptionStatus
    )
from .forms import (
    OrderInfoForm,
    OrderForm,
    OrderReserveForm,
    OrderRefundForm,
    OrderMemoEditFormFactory,
    ClientOptionalForm,
    TicketFormatSelectionForm,
 )
from .enqueue import (
    get_enqueue_each_print_action, 
    JoinedObjectsForProductItemDependentsProvider
)
from .helpers import decode_candidate_id
from .api import OrderAttributeIO

class OrderDependentsProvider(object):
    def __init__(self, request, order):
        self.request = request
        self.order = order
        self._dependents_provider = None

    @property
    def histories(self):
        order = self.order
        return DBSession.query(Order, include_deleted=True)\
            .options(undefer(Order.deleted_at))\
            .filter(Order.order_no==order.order_no)\
            .order_by(Order.branch_no.desc()).all()

    def get_order_attributes(self):
        return [(entry, False) for entry in OrderAttributeIO(include_undefined_items=True, mode='any').marshal(self.request, self.order)]

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

    def describe_objects_for_product_item_provider(self, ticket_format_id=None): #todo:rename
        if self._dependents_provider is None:
            order_id = self.order.id
            qs = DBSession.query(OrderedProduct, include_deleted=True).filter(OrderedProduct.order_id==order_id)
            qs = qs.join(OrderedProductItem).join(ProductItem, OrderedProductItem.product_item_id==ProductItem.id)
            qs = qs.outerjoin(OrderedProductItemToken, OrderedProductItem.id==OrderedProductItemToken.ordered_product_item_id)
            qs = qs.outerjoin(TicketBundle, ProductItem.ticket_bundle_id==TicketBundle.id)
            qs = qs.outerjoin(Seat, OrderedProductItemToken.seat_id==Seat.id)
            qs = qs.with_entities(OrderedProduct, OrderedProductItem, ProductItem, TicketBundle, Seat, OrderedProductItemToken)
            qs = qs.options(joinedload(ProductItem.product, Product.sales_segment))
            objs = qs.all()
            self._dependents_provider = JoinedObjectsForProductItemDependentsProvider(objs, ticket_format_id)
        return self._dependents_provider


class OrderShowFormProvider(object):
    def __init__(self, context):
        self.context = context
        self.order = context.order

    def get_order_info_form(self):
        order = self.order
        return OrderInfoForm(record_to_multidict(order), context=self.context)

    def get_shipping_address_form(self):
        order = self.order
        if order.shipping_address:
            form_shipping_address = ClientOptionalForm(record_to_multidict(order.shipping_address), context=self.context)
            form_shipping_address.tel_1.data = order.shipping_address.tel_1
            form_shipping_address.email_1.data = order.shipping_address.email_1
            form_shipping_address.email_2.data = order.shipping_address.email_2
        else:
            form_shipping_address = ClientOptionalForm(context=self.context)
        return form_shipping_address

    def get_order_form(self):
        order = self.order        
        return OrderForm(record_to_multidict(order), context=self.context)

    def get_order_reserve_form(self):
        order = self.order        
        return OrderReserveForm(performance_id=order.performance_id, request=self.context.request)

    def get_order_refund_form(self):
        order = self.order        
        return OrderRefundForm(MultiDict(payment_method_id=order.payment_delivery_pair.payment_method.id), organization_id=order.organization_id)

    def get_order_edit_attribute(self):
        return OrderMemoEditFormFactory(3)()

    def get_each_print_form(self, default_ticket_format_id):
        form = TicketFormatSelectionForm(context=self.context)
        if default_ticket_format_id is not None:
            form.ticket_format_id.data = default_ticket_format_id
        return form

class SingleOrderResource(TicketingAdminResource):
    @property
    def order(self):
        return None

    @property
    def available_ticket_formats(self):
        pass

    @reify
    def default_ticket_format(self):
        for ticket_format in self.available_ticket_formats:
            if self.order.payment_delivery_method_pair.delivery_method in ticket_format.delivery_methods:
              return ticket_format
        return self.available_ticket_formats[0] if self.available_ticket_formats else None

class MultipleOrdersResource(TicketingAdminResource):
    @property
    def orders(self):
        return None

    @reify
    def default_ticket_format(self):
        candidates = []
        orders = self.orders
        for ticket_format in self.available_ticket_formats:
            candidates.append(
                (
                    ticket_format,
                    sum(
                        any(
                            order.payment_delivery_method_pair.delivery_method == delivery_method
                            for delivery_method in ticket_format.delivery_methods
                            )
                        for order in orders
                        ),
                    ticket_format.name
                    )
                )
        candidates.sort(key=lambda a: -a[1])
        return candidates[0][0]


class OrderResource(SingleOrderResource):
    @reify
    def order_id(self):
        return int(self.request.matchdict.get('order_id', 0))
    
    @reify
    def order(self):
        order_history_id = self.request.GET.get("order_history")
        if order_history_id is not None:
            q = DBSession.query(Order, include_deleted=True) \
                .filter(Order.id == order_history_id, Order.organization_id == self.organization.id)
        else:
            Order_ = aliased(Order)
            q = DBSession.query(Order, include_deleted=True) \
                .join(Order_, Order.order_no == Order_.order_no) \
                .filter(Order.deleted_at == None) \
                .filter(Order.organization_id == self.organization.id) \
                .order_by(desc(Order.branch_no))
            q = q.filter(Order_.id == self.order_id, Order_.organization_id == self.organization.id)
        q = q.options(undefer(Order.deleted_at), undefer(Order.updated_at), undefer(Order.created_at), undefer(Order.queued))
        return q.first()

    @reify
    def available_ticket_formats(self):
        return TicketFormat.query\
            .options(joinedload(TicketFormat.delivery_methods)) \
            .filter(TicketFormat.id==Ticket.ticket_format_id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProduct.order_id == self.order.id)\
            .distinct(TicketFormat.id) \
            .all()


class OrderPrintByTokenActionProvider(object):
    def __init__(self, order, ticket_format_id):
        self.order = order
        self.ticket_format_id = ticket_format_id

    def get_print_candidate_action(self, candidate_id_list):
        candidate_id_list = [decode_candidate_id(xs) for xs in candidate_id_list]
        return get_enqueue_each_print_action(self.order, self.ticket_format_id, candidate_id_list)


class OrderPrintEachResource(OrderResource):
    def get_dependents_actions(self, order, ticket_format_id=None):
        return OrderPrintByTokenActionProvider(order, ticket_format_id)

    def get_dependents_models(self):
        return OrderDependentsProvider(self.request, self.order)

    def refresh_tokens(self, order, token_id_list, now):
        assert unicode(order.organization_id) == unicode(self.organization.id)
        tokens = (OrderedProductItemToken.query
                  .filter(OrderedProduct.order_id == order.id)
                  .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)
                  .filter(OrderedProductItemToken.ordered_product_item_id==OrderedProductItem.id)
                  .filter(OrderedProductItemToken.id.in_(token_id_list)).all())
        for t in tokens:
            t.refreshed_at = now
        order.printed_at = None


class OrdersShowResource(OrderResource):
    def get_dependents_models(self):
        return OrderDependentsProvider(self.request, self.order)

    def get_dependents_forms(self):
        return OrderShowFormProvider(self)


class CheckedOrderResource(MultipleOrdersResource):
    def __init__(self, request):
        super(CheckedOrderResource, self).__init__(request)
        self.order_ids = [o.lstrip('o:') for o in self.request.session.get('orders', []) if o.startswith('o:')]

    @reify
    def orders(self):
        return Order.query.filter(Order.id.in_(self.order_ids))


class SingleOrderEnqueueingResource(OrderResource):
    def __init__(self, request):
        super(SingleOrderEnqueueingResource, self).__init__(request)

    @reify
    def available_ticket_formats(self):
        return TicketFormat.query\
            .options(joinedload(TicketFormat.delivery_methods)) \
            .filter(TicketFormat.id==Ticket.ticket_format_id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProduct.order_id == self.order_id)\
            .distinct(TicketFormat.id) \
            .all()


class OrdersEnqueueingResource(CheckedOrderResource):
    def __init__(self, request):
        super(OrdersEnqueueingResource, self).__init__(request)

    @reify
    def available_ticket_formats(self):
        return TicketFormat.query\
            .options(joinedload(TicketFormat.delivery_methods)) \
            .filter(TicketFormat.id==Ticket.ticket_format_id)\
            .filter(Ticket.id==Ticket_TicketBundle.ticket_id)\
            .filter(Ticket_TicketBundle.ticket_bundle_id==TicketBundle.id)\
            .filter(TicketBundle.id==ProductItem.ticket_bundle_id)\
            .filter(ProductItem.id==OrderedProductItem.product_item_id)\
            .filter(OrderedProductItem.ordered_product_id==OrderedProduct.id)\
            .filter(OrderedProduct.order_id.in_(self.order_ids))\
            .distinct(TicketFormat.id) \
            .all()


class OrderedProductItemPreviewResource(SingleOrderResource):
    def __init__(self, request):
        super(OrderedProductItemPreviewResource, self).__init__(request)
        self.ordered_product_item_id = self.request.matchdict['item_id']
        self.ticket_format_id = self.request.matchdict['ticket_format_id']

    @reify
    def order(self):
        return self.ordered_product_item.ordered_product.order

    @reify
    def ordered_product_item(self):
        return OrderedProductItem.query.filter_by(id=self.ordered_product_item_id).one()

    @reify
    def ticket_format(self):
        if self.ticket_format_id is None:
            return None
        else:
            return TicketFormat.query.filter_by(id=self.ticket_format_id).one()

    @reify
    def available_ticket_formats(self):
        delivery_method_id = self.ordered_product_item.ordered_product.order.payment_delivery_pair.delivery_method_id
        bundle_id = self.ordered_product_item.product_item.ticket_bundle_id
        return TicketFormat.query\
            .options(joinedload(TicketFormat.delivery_methods)) \
            .filter(bundle_id==Ticket_TicketBundle.ticket_bundle_id, 
                    Ticket_TicketBundle.ticket_id==Ticket.id, 
                    Ticket.ticket_format_id==TicketFormat.id, 
                    TicketFormat_DeliveryMethod.delivery_method_id==delivery_method_id, 
                    TicketFormat.id==TicketFormat_DeliveryMethod.ticket_format_id)\
            .distinct(TicketFormat.id) \
            .all()

class CoverPreviewResource(OrderResource):
    def __init__(self, request):
        super(CoverPreviewResource, self).__init__(request)
        self.ticket_format_id = self.request.matchdict['ticket_format_id']

    @reify
    def ticket_format(self):
        if self.ticket_format_id is None:
            return None
        else:
            return TicketFormat.query.filter_by(id=self.ticket_format_id).one()
