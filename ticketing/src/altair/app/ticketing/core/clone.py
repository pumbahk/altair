# encoding: utf-8

import json
from datetime import datetime
from zope.interface import implementer

from .models import (
    Event,
    Stock,
    StockStatus,
    StockType,
    StockHolder,
    SalesSegmentGroup,
    SalesSegmentGroupSetting,
    PaymentDeliveryMethodPair,
    TicketBundle,
    Ticket_TicketBundle,
    TicketBundleAttribute,
    Ticket,
    EventSetting,
    Performance,
    PerformanceSetting,
    SalesSegment,
    SalesSegment_PaymentDeliveryMethodPair,
    SalesSegmentSetting,
    Product,
    ProductItem,
    Venue,
    VenueArea,
    VenueArea_group_l0_id,
    Seat,
    SeatAttribute,
    SeatStatus,
    SeatStatusEnum,
    SeatIndexType,
    SeatIndex,
    )
from altair.app.ticketing.lots.models import (
    Lot,
    LotStatusEnum,
    )
from altair.app.ticketing.users.models import (
    MemberGroup_SalesSegment,
    MemberGroup_SalesSegmentGroup,
    )

from .interfaces import ICoreModelTraverser


class StringGenerators(object):
    def generate_event_code(self, event):
        return event.code

    def generate_event_title(self, event):
        return u'%s (コピー)' % event.title

    def generate_event_abbreviated_title(self, event):
        return event.abbreviated_title

class Descriptor(object):
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src


class Backpatch(object):
    def __init__(self, dst, column_src_pairs):
        self.dst = dst
        self.column_src_pairs = column_src_pairs


@implementer(ICoreModelTraverser)
class CoreModelCloner(object):
    def __init__(self, handler, string_gen, organization, now=None):
        if now is None:
            now = datetime.now()
        self.now = now
        self.event = None
        self.sales_segment_group = None
        self.sales_segment = None
        self.ticket_bundle = None
        self.performance = None
        self.product = None
        self.venue = None
        self.seat = None
        self.lot = None
        self.handler = handler
        self.string_gen = string_gen
        self.organization = organization
        self.model_map = {}
        self.reverse_model_map = {}
        self.backpatches = []

    def _dump_json(self, o):
        return json.dumps(o, ensure_ascii=True) 

    def _add_to_model_map(self, src, dst):
        self.model_map[src] = dst
        self.reverse_model_map[dst] = src

    def _new_id(self, src):
        if src[1] == None:
            return None
        else:
            return self.model_map[src] 

    def _dispose(self, dst):
        src = self.reverse_model_map.get(dst)
        if src is not None:
            del self.reverse_model_map[dst]
            del self.model_map[src]
        dst.release()
        return src

    def begin_event(self, event):
        assert self.event is None
        if event.organization_id != self.organization.id:
            raise ValueError('event.organization_id != organization.id')
        event_id = self.handler.emit_insert_and_fetch_id(
            Event.__table__,
            {
                'id': None,
                'code': self.string_gen.generate_event_code(event),
                'title': self.string_gen.generate_event_title(event),
                'abbreviated_title': self.string_gen.generate_event_abbreviated_title(event),
                'account_id': event.account_id,
                'organization_id': event.organization_id,
                'cms_send_at': None,
                'display_order': 0,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.event = Descriptor(event_id, event)

    def end_event(self, event):
        for backpatch in self.backpatches:
            params = dict(
                (column, self._new_id(src))
                for column, src in backpatch.column_src_pairs
                )
            if 'updated_at' in backpatch.dst[0].c:
                params['updated_at'] = self.now
            self.handler.emit_update(
                backpatch.dst[0],
                'id', backpatch.dst[1],
                params
                )
        self._dispose(self.event.dst)
        self.event = None

    def visit_event_setting(self, event_setting):
        self.handler.emit_insert(
            EventSetting.__table__,
            {
                'event_id': self.event.dst,
                'order_limit': event_setting.order_limit,
                'max_quantity_per_user': event_setting.max_quantity_per_user,
                'middle_stock_threshold': event_setting.middle_stock_threshold,
                'middle_stock_threshold_percent': event_setting.middle_stock_threshold_percent,
                'cart_setting_id': event_setting.cart_setting_id,
                'visible': True,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def begin_sales_segment_group(self, sales_segment_group):
        assert self.sales_segment_group is None
        if sales_segment_group.organization_id != self.organization.id:
            raise ValueError('sales_segment_group.organization_id != self.organization.id')
        sales_segment_group_id = self.handler.emit_insert_and_fetch_id(
            SalesSegmentGroup.__table__,
            {
                'id': None,
                'event_id': self.event.dst,
                'name': sales_segment_group.name,
                'kind': sales_segment_group.kind,
                'start_at': sales_segment_group.start_at,
                'end_at': sales_segment_group.end_at,
                'upper_limit': sales_segment_group.max_quantity,
                'product_limit': sales_segment_group.max_product_quatity,
                'seat_choice': sales_segment_group.seat_choice,
                'public': sales_segment_group.public,
                'reporting': sales_segment_group.reporting,
                'margin_ratio': sales_segment_group.margin_ratio,
                'refund_ratio': sales_segment_group.refund_ratio,
                'printing_fee': sales_segment_group.printing_fee,
                'registration_fee': sales_segment_group.registration_fee,
                'account_id': sales_segment_group.account_id,
                'auth3d_notice': sales_segment_group.auth3d_notice,
                'organization_id': sales_segment_group.organization_id,
                'start_day_prior_to_performance': sales_segment_group.start_day_prior_to_performance,
                'start_time': sales_segment_group.start_time,
                'end_day_prior_to_performance': sales_segment_group.end_day_prior_to_performance,
                'end_time': sales_segment_group.end_time,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        for member_group in sales_segment_group.membergroups:
            self.handler.emit_insert(
                MemberGroup_SalesSegmentGroup,
                {
                    'id': None,
                    'membergroup_id': member_group.id,
                    'sales_segment_group_id': sales_segment_group_id,
                    }
                )
        self.sales_segment_group = Descriptor(sales_segment_group_id, sales_segment_group)
        self._add_to_model_map((SalesSegmentGroup.__table__, sales_segment_group.id), sales_segment_group_id)

    def end_sales_segment_group(self, sales_segment_group):
        self.sales_segment_group = None

    def visit_sales_segment_group_setting(self, sales_segment_group_setting):
        self.handler.emit_insert(
            SalesSegmentGroupSetting.__table__,
            {
                'id': None,
                'sales_segment_group_id': self.sales_segment_group.dst,
                'order_limit': sales_segment_group_setting.order_limit,
                'max_quantity_per_user': sales_segment_group_setting.max_quantity_per_user,
                'disp_orderreview': sales_segment_group_setting.disp_orderreview,
                'disp_agreement': sales_segment_group_setting.disp_agreement,
                'agreement_body': sales_segment_group_setting.agreement_body,
                'display_seat_no': sales_segment_group_setting.display_seat_no,
                'sales_counter_selectable': sales_segment_group_setting.sales_counter_selectable,
                'extra_form_fields': self._dump_json(sales_segment_group_setting.extra_form_fields),
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def visit_stock_type(self, stock_type):
        stock_type_id = self.handler.emit_insert_and_fetch_id(
            StockType.__table__,
            {
                'id': None,
                'name': stock_type.name,
                'type': stock_type.type,
                'display': stock_type.display,
                'display_order': stock_type.display_order,
                'event_id': self.event.dst,
                'quantity_only': stock_type.quantity_only,
                'disp_reports': stock_type.disp_reports,
                'style': self._dump_json(stock_type.style),
                'description': stock_type.description,
                'min_quantity': stock_type.min_quantity,
                'max_quantity': stock_type.max_quantity,
                'min_product_quantity': stock_type.min_product_quantity,
                'max_product_quantity': stock_type.max_product_quantity,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((StockType.__table__, stock_type.id), stock_type_id)

    def visit_stock_holder(self, stock_holder):
        stock_holder_id = self.handler.emit_insert_and_fetch_id(
            StockHolder.__table__,
            {
                'id': None,
                'name': stock_holder.name,
                'event_id': self.event.dst,
                'account_id': stock_holder.account_id,
                'is_putback_target': stock_holder.is_putback_target,
                'style': self._dump_json(stock_holder.style),
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((StockHolder.__table__, stock_holder.id), stock_holder_id)

    def visit_payment_delivery_method_pair(self, payment_delivery_method_pair):
        payment_delivery_method_pair_id = self.handler.emit_insert_and_fetch_id(
            PaymentDeliveryMethodPair.__table__,
            {
                'id': None,
                'sales_segment_group_id': self.sales_segment_group.dst,
                'system_fee': payment_delivery_method_pair.system_fee,
                'system_fee_type': payment_delivery_method_pair.system_fee_type,
                'transaction_fee': payment_delivery_method_pair.transaction_fee,
                # '_delivery_fee': payment_delivery_method_pair._delivery_fee,
                'delivery_fee_per_order': payment_delivery_method_pair.delivery_fee_per_order,
                'delivery_fee_per_principal_ticket': payment_delivery_method_pair.delivery_fee_per_principal_ticket,
                'delivery_fee_per_subticket': payment_delivery_method_pair.delivery_fee_per_subticket,
                'discount': payment_delivery_method_pair.discount,
                'discount_unit': payment_delivery_method_pair.discount_unit,
                'payment_start_day_calculation_base': payment_delivery_method_pair.payment_start_day_calculation_base,
                'payment_start_in_days': payment_delivery_method_pair.payment_start_in_days,
                'payment_start_at': payment_delivery_method_pair.payment_start_at,
                'payment_due_day_calculation_base': payment_delivery_method_pair.payment_due_day_calculation_base,
                'payment_period_days': payment_delivery_method_pair.payment_period_days,
                'payment_due_at': payment_delivery_method_pair.payment_due_at,
                'issuing_start_day_calculation_base': payment_delivery_method_pair.issuing_start_day_calculation_base,
                'issuing_interval_days': payment_delivery_method_pair.issuing_interval_days,
                'issuing_start_at': payment_delivery_method_pair.issuing_start_at,
                'issuing_end_day_calculation_base': payment_delivery_method_pair.issuing_end_day_calculation_base,
                'issuing_end_in_days': payment_delivery_method_pair.issuing_end_in_days,
                'issuing_end_at': payment_delivery_method_pair.issuing_end_at,
                'unavailable_period_days': payment_delivery_method_pair.unavailable_period_days,
                'public': payment_delivery_method_pair.public,
                'payment_method_id': payment_delivery_method_pair.payment_method_id,
                'delivery_method_id': payment_delivery_method_pair.delivery_method_id,
                'special_fee_name': payment_delivery_method_pair.special_fee_name,
                'special_fee': payment_delivery_method_pair.special_fee,
                'special_fee_type': payment_delivery_method_pair.special_fee_type,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((PaymentDeliveryMethodPair.__table__, payment_delivery_method_pair.id), payment_delivery_method_pair_id)

    def begin_ticket_bundle(self, ticket_bundle):
        assert self.ticket_bundle is None
        ticket_bundle_id = self.handler.emit_insert_and_fetch_id(
            TicketBundle.__table__,
            {
                'id': None,
                'name': ticket_bundle.name,
                'event_id': self.event.dst,
                'operator_id': ticket_bundle.operator_id,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        for ticket in ticket_bundle.tickets:
            self.handler.emit_insert(
                Ticket_TicketBundle.__table__,
                {
                    'ticket_bundle_id': ticket_bundle_id,
                    'ticket_id': self._new_id((Ticket.__table__, ticket.id)),
                    }
                )
        self.ticket_bundle = Descriptor(ticket_bundle_id, ticket_bundle)

    def end_ticket_bundle(self, ticket_bundle):
        self._add_to_model_map((TicketBundle.__table__, ticket_bundle.id), self.ticket_bundle.dst)
        self.ticket_bundle = None

    def visit_ticket_bundle_attribute(self, ticket_bundle_attribute):
        self.handler.emit_insert(
            TicketBundleAttribute.__table__,
            {
                'id': None,
                'ticket_bundle_id': self.ticket_bundle.dst,
                'name': ticket_bundle_attribute.name,
                'value': ticket_bundle_attribute.value,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def visit_ticket(self, ticket):
        if ticket.organization_id != self.organization.id:
            raise ValueError('ticket.organization_id != self.organization.id')
        ticket_id = self.handler.emit_insert_and_fetch_id(
            Ticket.__table__,
            {
                'id': None, 
                'organization_id': ticket.organization_id,
                'event_id': self.event.dst,
                'ticket_format_id': ticket.ticket_format_id,
                'name': ticket.name,
                'flags': ticket.flags,
                'original_ticket_id': ticket.original_ticket_id,
                'base_template_id': ticket.base_template_id,
                'data': self._dump_json(ticket.data),
                'filename': ticket.filename,
                'cover_print': ticket.cover_print,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((Ticket.__table__, ticket.id), ticket_id)

    def begin_lot(self, lot):
        assert self.lot is None
        # if lot.organization_id != self.organization.id:
        #     raise ValueError('lot.organization_id != self.organization.id')
        lot_id = self.handler.emit_insert_and_fetch_id(
            Lot.__table__,
            {
                'id': None,
                'name': lot.name,
                'limit_wishes': lot.limit_wishes,
                'event_id': self.event.dst,
                'selection_type': lot.selection_type,
                'sales_segment_id': None,
                'status': LotStatusEnum.New,
                'description': lot.description,
                'entry_limit': lot.entry_limit,
                'lotting_announce_datetime': lot.lotting_announce_datetime,
                'lotting_announce_timezone': lot.lotting_announce_timezone,
                'custom_timezone_label': lot.custom_timezone_label,
                'system_fee': lot.system_fee,
                'organization_id': lot.organization_id,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.lot = Descriptor(lot_id, lot)
        self.backpatches.append(Backpatch((Lot.__table__, lot_id), [('sales_segment_id', (SalesSegment.__table__, lot.sales_segment_id))]))

    def end_lot(self, lot):
        self.lot = None

    def begin_performance(self, performance):
        assert self.performance is None
        performance_id = self.handler.emit_insert_and_fetch_id(
            Performance.__table__,
            {
                'id': None,
                'name': performance.name,
                'code': performance.code,
                'abbreviated_title': performance.abbreviated_title,
                'subtitle': performance.subtitle,
                'subtitle2': performance.subtitle2,
                'subtitle3': performance.subtitle3,
                'subtitle4': performance.subtitle4,
                'note': performance.note,
                'open_on': performance.open_on,
                'start_on': performance.start_on,
                'end_on': performance.end_on,
                'public': performance.public,
                'event_id': self.event.dst,
                'redirect_url_pc': performance.redirect_url_pc,
                'redirect_url_mobile': performance.redirect_url_mobile,
                'display_order': performance.display_order,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.performance = Descriptor(performance_id, performance)
        self._add_to_model_map((Performance.__table__, performance.id), performance_id)

    def end_performance(self, performance):
        self.performance = None

    def visit_performance_setting(self, performance_setting):
        self.handler.emit_insert(
            PerformanceSetting.__table__,
            {
                'id': None,
                'performance_id': self.performance.dst,
                'order_limit': performance_setting.order_limit,
                'entry_limit': performance_setting.entry_limit,
                'max_quantity_per_user': performance_setting.max_quantity_per_user,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def visit_stock(self, stock):
        stock_id = self.handler.emit_insert_and_fetch_id(
            Stock.__table__,
            {
                'id': None,
                'quantity': stock.quantity,
                'performance_id': self.performance.dst,
                'stock_holder_id': self._new_id((StockHolder.__table__, stock.stock_holder_id)),
                'stock_type_id': self._new_id((StockType.__table__, stock.stock_type_id)),
                'locked_at': stock.locked_at,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.handler.emit_insert(
            StockStatus.__table__,
            {
                'stock_id': stock_id,
                'quantity': stock.quantity,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((Stock.__table__, stock.id), stock_id)

    def begin_sales_segment(self, sales_segment):
        assert self.sales_segment is None
        if sales_segment.organization_id != self.organization.id:
            raise ValueError('sales_segment.organization_id != self.organization.id')
        sales_segment_id = self.handler.emit_insert_and_fetch_id(
            SalesSegment.__table__,
            {
                'id': None,
                'sales_segment_group_id': self.sales_segment_group.dst,
                'event_id': self.event.dst,
                'performance_id': None,
                'start_at': sales_segment.start_at,
                'end_at': sales_segment.end_at,
                'upper_limit': sales_segment.max_quantity,
                'product_limit': sales_segment.max_product_quatity,
                'seat_choice': sales_segment.seat_choice,
                'public': sales_segment.public,
                'reporting': sales_segment.reporting,
                'margin_ratio': sales_segment.margin_ratio,
                'refund_ratio': sales_segment.refund_ratio,
                'printing_fee': sales_segment.printing_fee,
                'registration_fee': sales_segment.registration_fee,
                'account_id': sales_segment.account_id,
                'auth3d_notice': sales_segment.auth3d_notice,
                'organization_id': sales_segment.organization_id,
                'use_default_seat_choice': sales_segment.use_default_seat_choice,
                'use_default_public': sales_segment.use_default_public,
                'use_default_reporting': sales_segment.use_default_reporting,
                'use_default_payment_delivery_method_pairs': sales_segment.use_default_payment_delivery_method_pairs,
                'use_default_start_at': sales_segment.use_default_start_at,
                'use_default_end_at': sales_segment.use_default_end_at,
                'use_default_upper_limit': sales_segment.use_default_max_quantity,
                'use_default_product_limit': sales_segment.use_default_max_product_quatity,
                'use_default_account_id': sales_segment.use_default_account_id,
                'use_default_margin_ratio': sales_segment.use_default_margin_ratio,
                'use_default_refund_ratio': sales_segment.use_default_refund_ratio,
                'use_default_printing_fee': sales_segment.use_default_printing_fee,
                'use_default_registration_fee': sales_segment.use_default_registration_fee,
                'use_default_auth3d_notice': sales_segment.use_default_auth3d_notice,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        for payment_delivery_method_pair in sales_segment.payment_delivery_method_pairs:
            self.handler.emit_insert(
                SalesSegment_PaymentDeliveryMethodPair,
                {
                    'id': None,
                    'payment_delivery_method_pair_id': self._new_id((PaymentDeliveryMethodPair.__table__, payment_delivery_method_pair.id)),
                    'sales_segment_id': sales_segment_id,
                    }
                )
        for member_group in sales_segment.membergroups:
            self.handler.emit_insert(
                MemberGroup_SalesSegment,
                {
                    'id': None,
                    'membergroup_id': member_group.id,
                    'sales_segment_id': sales_segment_id,
                    }
                )
        self.sales_segment = Descriptor(sales_segment_id, sales_segment)
        self.backpatches.append(Backpatch((SalesSegment.__table__, sales_segment_id), [('performance_id', (Performance.__table__, sales_segment.performance_id))]))
        self._add_to_model_map((SalesSegment.__table__, sales_segment.id), sales_segment_id)

    def end_sales_segment(self, sales_segment):
        self.sales_segment = None

    def visit_sales_segment_setting(self, sales_segment_setting):
        self.handler.emit_insert(
            SalesSegmentSetting.__table__,
            {
                'id': None,
                'sales_segment_id': self.sales_segment.dst,
                'order_limit': sales_segment_setting.order_limit,
                'max_quantity_per_user': sales_segment_setting.max_quantity_per_user,
                'disp_orderreview': sales_segment_setting.disp_orderreview,
                'disp_agreement': sales_segment_setting.disp_agreement,
                'agreement_body': sales_segment_setting.agreement_body,
                'display_seat_no': sales_segment_setting.display_seat_no,
                'sales_counter_selectable': sales_segment_setting.sales_counter_selectable,
                'extra_form_fields': self._dump_json(sales_segment_setting.extra_form_fields),
                'use_default_order_limit': sales_segment_setting.use_default_order_limit,
                'use_default_max_quantity_per_user': sales_segment_setting.use_default_max_quantity_per_user,
                'use_default_disp_orderreview': sales_segment_setting.use_default_disp_orderreview,
                'use_default_display_seat_no': sales_segment_setting.use_default_display_seat_no,
                'use_default_disp_agreement': sales_segment_setting.use_default_disp_agreement,
                'use_default_agreement_body': sales_segment_setting.use_default_agreement_body,
                'use_default_sales_counter_selectable': sales_segment_setting.use_default_sales_counter_selectable,
                'use_default_extra_form_fields': sales_segment_setting.use_default_extra_form_fields,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def begin_product(self, product):
        assert self.product is None
        product_id = self.handler.emit_insert_and_fetch_id(
            Product.__table__,
            {
                'id': None,
                'performance_id': None,
                'name': product.name,
                'price': product.price,
                'display_order': product.display_order,
                'sales_segment_group_id': product.sales_segment_group_id,
                'sales_segment_id': self.sales_segment.dst,
                'ticket_type_id': product.ticket_type_id,
                'seat_stock_type_id': self._new_id((StockType.__table__, product.seat_stock_type_id)),
                'event_id': product.event_id,
                'public': product.public,
                'description': product.description,
                'base_product_id': None,
                'min_product_quantity': product.min_product_quantity,
                'max_product_quantity': product.max_product_quantity,
                'augus_ticket_id': None, # XXX
                'must_be_chosen': product.must_be_chosen,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.backpatches.append(Backpatch((Product.__table__, product_id), [
            ('performance_id', (Performance.__table__, product.performance_id)),
            ('base_product_id', (Product.__table__, product.base_product_id))
            ]))
        self.product = Descriptor(product_id, product)

    def end_product(self, product):
        self.product = None

    def visit_product_item(self, product_item):
        product_item_id = self.handler.emit_insert_and_fetch_id(
            ProductItem.__table__,
            {
                'id': None,
                'name': product_item.name,
                'price': product_item.price,
                'product_id': self.product.dst,
                'performance_id': None,
                'stock_id': None,
                'quantity': product_item.quantity,
                'ticket_bundle_id': self._new_id((TicketBundle.__table__, product_item.ticket_bundle_id)),
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.backpatches.append(Backpatch((ProductItem.__table__, product_item_id), [
            ('performance_id', (Performance.__table__, product_item.performance_id)),
            ('stock_id', (Stock.__table__, product_item.stock_id)),
            ]))

    def begin_venue(self, venue):
        assert self.venue is None
        if venue.organization_id != self.organization.id:
            raise ValueError('venue.organization_id != self.organization.id')
        venue_id = self.handler.emit_insert_and_fetch_id(
            Venue.__table__,
            {
                'id': None,
                'site_id': venue.site_id,
                'performance_id': self.performance.dst,
                'organization_id': venue.organization_id,
                'name': venue.name,
                'sub_name': venue.sub_name,
                'original_venue_id': venue.original_venue_id,
                'attributes': self._dump_json(venue.attributes),
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.venue = Descriptor(venue_id, venue)

    def end_venue(self, venue):
        self.venue = None

    def visit_venue_area(self, venue_area):
        venue_area_id = self.handler.emit_insert_and_fetch_id(
            VenueArea.__table__,
            {
                'id': None,
                'name': venue_area.name,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        for group in set(venue_area.groups):
            self.handler.emit_insert(
                VenueArea_group_l0_id.__table__,
                {
                    'venue_id': self.venue.dst,
                    'group_l0_id': group.group_l0_id,
                    'venue_area_id': venue_area_id,
                    }
                )

    def begin_seat(self, seat):
        assert self.seat is None
        seat_id = self.handler.emit_insert_and_fetch_id(
            Seat.__table__,
            {
                'id': None,
                'l0_id': seat.l0_id,
                'name': seat.name,
                'seat_no': seat.seat_no,
                'stock_id': self._new_id((Stock.__table__, seat.stock_id)),
                'venue_id': self.venue.dst,
                'row_l0_id': seat.row_l0_id,
                'group_l0_id': seat.group_l0_id,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.handler.emit_insert(
            SeatStatus.__table__,
            {
                'seat_id': seat_id,
                'status': SeatStatusEnum.Vacant.v,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self.seat = Descriptor(seat_id, seat)

    def end_seat(self, seat):
        self._dispose(self.seat.dst)
        self.seat = None

    def visit_seat_attribute(self, seat_attribute):
        self.handler.emit_insert(
            SeatAttribute.__table__,
            {
                'seat_id': self.seat.dst,
                'name': seat_attribute.name,
                'value': seat_attribute.value,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )

    def visit_seat_index_type(self, seat_index_type):
        seat_index_type_id = self.handler.emit_insert_and_fetch_id(
            SeatIndexType.__table__,
            {
                'id': None,
                'venue_id': self.venue.dst,
                'name': seat_index_type.name,
                'created_at': self.now,
                'updated_at': self.now,
                }
            )
        self._add_to_model_map((SeatIndexType.__table__, seat_index_type.id), seat_index_type_id)

    def visit_seat_index(self, seat_index):
        self.handler.emit_insert(
            SeatIndex.__table__,
            {
                'seat_index_type_id': self._new_id((SeatIndexType.__table__, seat_index.seat_index_type_id)),
                'seat_id': self.seat.dst,
                'index': seat_index.index,
                }
            )

