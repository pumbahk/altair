# -*- coding:utf-8 -*-
import os
import shutil
import logging
import json
import urllib
import glob
from datetime import datetime
from .reservation_writer import ReservationReportWriter
from datetime import datetime
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response, FileResponse
from sqlalchemy.sql.expression import or_, desc
from sqlalchemy.orm import joinedload, joinedload_all, undefer, aliased

# from paste.util.multidict import MultiDict
from webob.multidict import MultiDict
from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.models import (
    DBSession,
    record_to_multidict,
    )

from altair.app.ticketing.core.models import (
    Performance,
    StockType,
    Stock,
    SalesSegment,
    ProductItem,
    Product,
    Seat,
    Venue,
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
    OrderReservePreconditionsForm,
    OrderReserveSettingsForm,
    OrderReserveSalesSegmentChooserForm,
    OrderReserveSeatsForm,
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
from altair.app.ticketing.payments import plugins
from .helpers import decode_candidate_id
from .api import OrderAttributeIO

logger = logging.getLogger(__name__)


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
        for_ = 'lots' if self.order.created_from_lot_entry else 'cart'
        return [(entry, False) for entry in OrderAttributeIO(include_undefined_items=True, mode='any', for_=for_).marshal(self.request, self.order)]

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

    def get_order_refund_form(self):
        order = self.order        
        return OrderRefundForm(MultiDict(payment_method_id=order.payment_delivery_pair.payment_method.id), context=self.context)

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

from altair.app.ticketing.events.performances.resources import SalesCounterResourceMixin


class ReservationReportResource(OrderResource):
    def create_reservation_report(self):
        """
        予約管理者の帳票機能
        """
        # 前回のファイルを削除(オペレータごと)
        var_dir = self.request.registry.settings.get('reservation.var_dir', False)
        delete_files = glob.glob('{0}./*.xls'.format(var_dir))
        for file in delete_files:
            os.remove(file)

        # 名前決定
        now = datetime.now()
        slave_session = get_db_session(self.request, name="slave")
        order_count = slave_session.query(Order).filter(Order.operator_id == self.user.id).count()
        file_name = u"{0}_{1}_{2:05d}.xls".format(self.user.name, now.strftime("%Y%m%d"), order_count).encode('utf-8')

        # ワークディレクトリにコピー
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates/orders")
        template_file = "{0}/{1}".format(template_dir, "reservation_report.xls")
        tmp_file = os.path.join("{0}{1}".format(var_dir, file_name))
        shutil.copyfile(template_file, tmp_file)

        writer = ReservationReportWriter(tmp_file, self.order, self.user)
        writer.write()

        # ダウンロード
        response = FileResponse(os.path.abspath(tmp_file))
        response.headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(file_name))
        ]
        return response


class OrderReserveResource(TicketingAdminResource, SalesCounterResourceMixin):
    def __init__(self, request):
        super(OrderReserveResource, self).__init__(request)
        self.now = datetime.now()

        self.preconditions_form = OrderReservePreconditionsForm(self.request.POST, context=self)
        if not self.preconditions_form.validate():
            logger.debug('%r' % self.preconditions_form.errors)
            self.raise_error(u'不正な値が指定されました')

        # パフォーマンスの取得
        self.performance = DBSession.query(Performance).filter(Performance.id == self.preconditions_form.performance_id.data).one()

        self.seats_form = OrderReserveSeatsForm(self.request.POST, context=self)
        if not self.seats_form.validate():
            logger.debug('%r' % self.seats_form.errors)
            self.raise_error(u'不正な値が指定されました')

        # stockの取得
        stock_ids = []
        try:
            stock_ids = [long(stock_id) for stock_id in self.preconditions_form.stocks.data]
        except (TypeError, ValueError):
            pass
        self.stocks = DBSession.query(Stock).options(joinedload(Stock.stock_type)).filter(Stock.id.in_(stock_ids)).all()

        # seat l0_idの取得
        seat_l0_ids = self.seats_form.seats.data

        # 選択可能なsales_segmentの取得
        applicable_sales_segment_ids = None
        if seat_l0_ids:
            applicable_sales_segment_ids = set(
                x[0]
                for x in DBSession.query(SalesSegment.id) \
                        .join(SalesSegment.products) \
                        .join(Product.items) \
                        .join(ProductItem.stock) \
                        .join(Stock.seats) \
                        .join(Seat.venue) \
                        .filter(Stock.performance_id == self.performance.id) \
                        .filter(Venue.performance_id == self.performance.id) \
                        .filter(Seat.l0_id.in_(seat_l0_ids)) \
                        .distinct()
                )
        elif stock_ids:
            applicable_sales_segment_ids = set(
                x[0]
                for x in DBSession.query(SalesSegment.id) \
                        .join(SalesSegment.products) \
                        .join(Product.items) \
                        .join(ProductItem.stock) \
                        .filter(Stock.id.in_(stock_ids)) \
                        .distinct()
                )
        if applicable_sales_segment_ids is not None:
            sales_segments = [sales_segment for sales_segment in self.available_sales_segments if sales_segment.id in applicable_sales_segment_ids]
        else:
            sales_segments = self.available_sales_segments
        self.sales_segments = sales_segments

        self.settings_form = OrderReserveSettingsForm(self.request.POST, context=self)
        sales_segment_id = self.settings_form.sales_segment_id.data
        sales_segment = None
        if not self.settings_form.validate():
            self.settings_form.clear_errors()
            sales_segment = sales_segments[0]
            self.settings_form.sales_segment_id.data = sales_segment.id
        else:
            if sales_segment_id is not None:
                sales_segment = DBSession.query(SalesSegment) \
                    .filter(SalesSegment.performance_id == self.performance.id) \
                    .filter(SalesSegment.id == sales_segment_id) \
                    .one()
                if sales_segment not in self.available_sales_segments:
                    raise HTTPBadRequest()
        self.sales_segment = sales_segment

        if seat_l0_ids:
            q = DBSession.query(Product) \
                .join(Product.seat_stock_type) \
                .join(Product.sales_segment) \
                .join(StockType.stocks) \
                .join(Stock.seats) \
                .join(Seat.venue) \
                .filter(SalesSegment.performance_id == self.performance.id) \
                .filter(Stock.performance_id == self.performance.id) \
                .filter(Venue.performance_id == self.performance.id) \
                .filter(Seat.l0_id.in_(seat_l0_ids))
        else:
            q = DBSession.query(Product) \
                .join(Product.sales_segment) \
                .filter(SalesSegment.performance_id == self.performance.id)
        if sales_segment is not None:
            q = q.filter(Product.sales_segment_id == sales_segment.id)
        if len(stock_ids) > 0:
            q = q.join(Product.items).filter(ProductItem.stock_id.in_(stock_ids))
        self.products = q.distinct().all()
        self.form = OrderReserveForm(self.request.POST, context=self)

    @reify
    def stock_types(self):
        return set(product.seat_stock_type for product in self.products) 

    @reify
    def seats(self):
        return list(DBSession.query(Seat).filter(Seat.venue_id == self.performance.venue.id, Seat.l0_id.in_(self.seats_form.seats.data)))

    def raise_error(self, message, klass=HTTPBadRequest):
        raise klass(
            content_type='application/json',
            text=json.dumps(dict(message=message), ensure_ascii=False)
            )

    @reify
    def payment_delivery_method_pairs(self):
        return sorted(
            (
                payment_delivery_method_pair
                for payment_delivery_method_pair in self.sales_segment.payment_delivery_method_pairs
                ),
            key=lambda x: (x.payment_method.payment_plugin_id == plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID),
            reverse=True
            )

    @reify
    def convenience_payment_delivery_method_pairs(self):
        return [
            payment_delivery_method_pair
            for payment_delivery_method_pair in self.payment_delivery_method_pairs
            if payment_delivery_method_pair.payment_method.pay_at_store() or \
               payment_delivery_method_pair.delivery_method.deliver_at_store()
            ]

class OrderReservePageResource(TicketingAdminResource, SalesCounterResourceMixin):
    def __init__(self, request):
        super(OrderReservePageResource, self).__init__(request)
        self.now = datetime.now()

        self.preconditions_form = OrderReservePreconditionsForm(self.request.POST, context=self)
        if not self.preconditions_form.validate():
            logger.debug('%r' % self.preconditions_form.errors)
            self.raise_error(u'不正な値が指定されました')

        # パフォーマンスの取得
        self.performance = DBSession.query(Performance).filter(Performance.id == self.preconditions_form.performance_id.data).one()

        self.seats_form = OrderReserveSeatsForm(self.request.POST, context=self)
        if not self.seats_form.validate():
            logger.debug('%r' % self.seats_form.errors)
            self.raise_error(u'不正な値が指定されました')

        # stockの取得
        stock_ids = []
        try:
            stock_ids = [long(stock_id) for stock_id in self.preconditions_form.stocks.data]
        except (TypeError, ValueError):
            pass
        self.stocks = DBSession.query(Stock).options(joinedload(Stock.stock_type)).filter(Stock.id.in_(stock_ids)).all()

        self.sales_segments = self.available_sales_segments

        self.settings_form = OrderReserveSalesSegmentChooserForm(self.request.POST, context=self)
        if not self.settings_form.validate():
            logger.debug('%r' % self.settings_form.errors)
            self.raise_error(u'不正な値が指定されました')

        sales_segment_id = self.settings_form.sales_segment_id.data
        sales_segment = None
        if sales_segment_id is not None:
            sales_segment = DBSession.query(SalesSegment) \
                .filter(SalesSegment.performance_id == self.performance.id) \
                .filter(SalesSegment.id == sales_segment_id) \
                .one()
            if sales_segment not in self.available_sales_segments:
                raise HTTPBadRequest()
        self.sales_segment = sales_segment

        q = DBSession.query(Product) \
            .join(Product.sales_segment) \
            .options(
                joinedload_all(Product.items, ProductItem.stock, Stock.stock_status),
                joinedload(Product.items, ProductItem.stock, Stock.stock_holder)
                )\
            .filter(SalesSegment.performance_id == self.performance.id)
        if sales_segment is not None:
            q = q.filter(Product.sales_segment_id == sales_segment.id)
        if len(stock_ids) > 0:
            q = q.join(Product.items).filter(ProductItem.stock_id.in_(stock_ids))
        self.products = q.distinct().all()

    def raise_error(self, message, klass=HTTPBadRequest):
        raise klass(
            content_type='application/json',
            text=json.dumps(dict(message=message), ensure_ascii=False)
            )
