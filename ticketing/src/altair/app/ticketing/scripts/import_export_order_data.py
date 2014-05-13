from pyramid.paster import setup_logging, bootstrap
import sys
import argparse
from sqlalchemy import sql, orm
from datetime import date, datetime
from decimal import Decimal
from collections import OrderedDict
import json

def do_import(request, session, organization, event, performance, order_nos):
    pass

def format_datetime(dt):
    return dt.isoformat() if dt is not None else None

class listwrap(list):
    def __init__(self, o):
        self.o = o

    def __bool__(self):
        return True

    def __len__(selF):
        return 1

    def __iter__(self):
        return iter(self.o)

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return format_datetime(o)
        elif isinstance(o, Decimal):
            return unicode(o.quantize(0))
        else:
            try:
                i = iter(o)
                return listwrap(i)
            except TypeError:
                raise super(MyJSONEncoder, self).default(o)

def make_shipping_address_dict(shipping_address):
    return OrderedDict((
        ('id', shipping_address.id),
        ('user_id', shipping_address.user_id),
        ('emails', shipping_address.emails),
        ('nick_name', shipping_address.nick_name),
        ('first_name', shipping_address.first_name),
        ('last_name', shipping_address.last_name),
        ('first_name_kana', shipping_address.first_name_kana),
        ('last_name_kana', shipping_address.last_name_kana),
        ('zip', shipping_address.zip),
        ('country', shipping_address.country),
        ('prefecture', shipping_address.prefecture),
        ('city', shipping_address.city),
        ('address_1', shipping_address.address_1),
        ('address_2', shipping_address.address_2),
        ('tel_1', shipping_address.tel_1),
        ('tel_2', shipping_address.tel_2),
        ('fax', shipping_address.fax),
        ('created_at', shipping_address.created_at),
        ('updated_at', shipping_address.updated_at),
        ))

def make_user_profile_dict(user_profile):
    return OrderedDict((
        ('user_id', user_profile.user_id),
        ('emails', user_profile.emails),
        ('nick_name', user_profile.nick_name),
        ('first_name', user_profile.first_name),
        ('last_name', user_profile.last_name),
        ('first_name_kana', user_profile.first_name_kana),
        ('last_name_kana', user_profile.last_name_kana),
        ('sex', user_profile.sex),
        ('zip', user_profile.zip),
        ('country', user_profile.country),
        ('prefecture', user_profile.prefecture),
        ('city', user_profile.city),
        ('address_1', user_profile.address_1),
        ('address_2', user_profile.address_2),
        ('tel_1', user_profile.tel_1),
        ('tel_2', user_profile.tel_2),
        ('fax', user_profile.fax),
        ('created_at', user_profile.created_at),
        ('updated_at', user_profile.updated_at),
        ))

def make_seat_dict(seat):
    return OrderedDict((
        ('id', seat.id),
        ('stock_id', seat.stock_id),
        ('venue_id', seat.venue_id),
        ('row_l0_id', seat.row_l0_id),
        ('group_l0_id', seat.group_l0_id),
        ('attributes', dict(seat.attributes)),
        ('status', seat.status),
        ('created_at', seat.created_at),
        ('updated_at', seat.updated_at),
        ))

def make_token_dict(token):
    return OrderedDict((
        ('id', token.id),
        ('serial', token.serial),
        ('seat_id', token.seat_id),
        ('*seat', make_seat_dict(token.seat) if token.seat else None),
        ('valid', token.valid),
        ('issued_at', token.issued_at),
        ('printed_at', token.printed_at),
        ('refreshed_at', token.refreshed_at),
        ))

def make_stock_type_dict(stock_type):
    return OrderedDict((
        ('id', stock_type.id),
        ('name', stock_type.name),
        ('type', stock_type.type),
        ('display', stock_type.display),
        ('display_order', stock_type.display_order),
        ('quantity_only', stock_type.quantity_only),
        ('style', dict(stock_type.style)),
        ('description', stock_type.description),
        ('min_quantity', stock_type.min_quantity),
        ('max_quantity', stock_type.max_quantity),
        ('min_product_quantity', stock_type.min_product_quantity),
        ('max_product_quantity', stock_type.max_product_quantity),
        ('created_at', stock_type.created_at),
        ('updated_at', stock_type.updated_at),
        ))

def make_stock_holder_dict(stock_holder):
    return OrderedDict((
        ('id', stock_holder.id),
        ('name', stock_holder.name),
        ('account_id', stock_holder.account_id),
        ('style', dict(stock_holder.style)),
        ('created_at', stock_holder.created_at),
        ('updated_at', stock_holder.updated_at),
        ))

def make_stock_dict(stock):
    return OrderedDict((
        ('id', stock.id),
        ('stock_holder_id', stock.stock_holder_id),
        ('*stock_holder', make_stock_holder_dict(stock.stock_holder)),
        ('stock_type_id', stock.stock_type_id),
        ('*stock_type', make_stock_type_dict(stock.stock_type)),
        ('quantity', stock.quantity),
        ('available_quantity', stock.stock_status.quantity),
        ('locked_at', stock.locked_at),
        ('created_at', stock.created_at),
        ('updated_at', stock.updated_at),
        ))

def make_ticket_bundle_dict(ticket_bundle):
    tickets_dict = {}
    for ticket in ticket_bundle.tickets:
        tickets_dict.setdefault(ticket.ticket_format_id, []).append(
            { 'ticket_id': ticket.id }
            )
    return OrderedDict((
        ('id', ticket_bundle.id),
        ('operator_id', ticket_bundle.operator_id),
        ('tickets', tickets_dict),
        ('attributes', dict(ticket_bundle.attributes)),
        ))

def make_product_item_dict(product_item):
    return OrderedDict((
        ('id', product_item.id),
        ('name', product_item.name),
        ('price', product_item.price),
        ('performance_id', product_item.performance_id),
        ('stock_id', product_item.stock_id),
        ('*stock', make_stock_dict(product_item.stock)),
        ('quantity', product_item.quantity),
        ('ticket_bundle_id', product_item.ticket_bundle_id),
        ('*ticket_bundle', make_ticket_bundle_dict(product_item.ticket_bundle)),
        ('created_at', product_item.created_at),
        ('updated_at', product_item.updated_at),
        ))

def make_product_dict(product):
    return OrderedDict((
        ('id', product.id),
        ('name', product.name),
        ('price', product.price),
        ('display_order', product.display_order),
        ('sales_segment_group_id', product.sales_segment_group_id),
        ('sales_segment_id', product.sales_segment_id),
        ('seat_stock_type_id', product.seat_stock_type_id),
        ('event_id', product.event_id),
        ('public', product.public),
        ('base_product_id', product.base_product_id),
        ('min_product_quantity', product.min_product_quantity),
        ('max_product_quantity', product.max_product_quantity),
        ('augus_ticket_id', product.augus_ticket_id),
        ('description', product.description),
        ('created_at', product.created_at),
        ('updated_at', product.updated_at),
        ))

def make_ordered_product_item_dict(element):
    return OrderedDict((
        ('id', element.id),
        ('product_item_id', element.product_item_id),
        ('*product_item', make_product_item_dict(element.product_item)),
        ('price', element.price),
        ('quantity', element.quantity),
        ('issued_at', element.issued_at),
        ('printed_at', element.printed_at),
        ('attributes', dict(element.attributes)),
        ('seats', [
            make_seat_dict(seat)
            for seat in element.seats
            ]),
        ('tokens', [
            make_token_dict(token)
            for token in element.tokens
            ]),
        ))

def make_ordered_product_dict(item):
    return OrderedDict((
        ('id', item.id),
        ('proto_order_id', item.proto_order_id),
        ('product_id', item.product_id),
        ('*product', make_product_dict(item.product)),
        ('price', item.price),
        ('quantity', item.quantity),
        ('elements', [
            make_ordered_product_item_dict(element)
            for element in item.elements
            ]),
        ))

def make_order_dict(order):
    return OrderedDict((
        ('id', order.id),
        ('order_no', order.order_no),
        ('branch_no', order.branch_no),
        ('organization_id', order.organization_id),
        ('sales_segment_id', order.sales_segment_id),
        ('*user_profile', make_user_profile_dict(order.user.user_profile) if order.user else None),
        ('*shipping_address', make_shipping_address_dict(order.shipping_address) if order.shipping_address_id else None),
        ('operator_id', order.operator_id),
        ('channel', order.channel),
        ('total_amount', order.total_amount),
        ('system_fee', order.system_fee),
        ('special_fee_name', order.special_fee_name),
        ('special_fee', order.special_fee),
        ('transaction_fee', order.transaction_fee),
        ('delivery_fee', order.delivery_fee),
        ('payment_delivery_method_pair_id', order.payment_delivery_method_pair_id),
        ('paid_at', order.paid_at),
        ('delivered_at', order.delivered_at),
        ('canceled_at', order.canceled_at),
        ('refunded_at', order.refunded_at),
        ('issued', order.issued),
        ('issued_at', order.issued_at),
        ('printed_at', order.printed_at),
        ('issuing_start_at', order.issuing_start_at),
        ('issuing_end_at', order.issuing_end_at),
        ('payment_start_at', order.payment_start_at),
        ('payment_due_at', order.payment_due_at),
        ('browserid', order.browserid),
        ('note', order.note),
        ('items', [
            make_ordered_product_dict(item)
            for item in order.items
            ]),
        ('attributes', dict(order.attributes)),
        ))

def do_export(request, session, organization, event, performance, order_nos):
    from altair.app.ticketing.orders.models import (
        Order,
        OrderedProduct,
        OrderedProductItem,
        OrderedProductItemToken,
        orders_seat_table
        )
    from altair.app.ticketing.users.models import User
    from altair.app.ticketing.core.models import (
        Organization,
        Event,
        Performance,
        )
    q = session.query(Order) \
        .options(
            orm.joinedload('user'),
            orm.joinedload('user.user_profile'),
            orm.joinedload('shipping_address'),
            orm.joinedload('items'),
            orm.joinedload('items.elements'),
            orm.joinedload('items.elements.tokens'),
            orm.joinedload('items.elements.seats')
            )
    if organization:
        q = q.filter(Order.organization_id == organization.id)
    if event:
        q = q.join(Order.performance).filter(Performance.event_id == event.id)
    if performance:
        q = q.filter(Order.performance_id == performance.id)
    if order_nos:
        q = q.filter(Order.order_no.in_(order_nos))

    encoder = MyJSONEncoder(ensure_ascii=False, indent=True)
    out = sys.stdout
    for chunk in encoder.iterencode(make_order_dict(order) for order in q):
        out.write(chunk.encode('utf-8'))

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-O', '--organization', metavar='organization', type=str)
    parser.add_argument('-E', '--event', metavar='event', type=str)
    parser.add_argument('-P', '--performance', metavar='performance', type=str)
    parser.add_argument('mode', type=str)
    parser.add_argument('order_no', metavar='order_no', type=str, nargs='*')
    args = parser.parse_args()
    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    from sqlahelper import get_session
    session = get_session()
    from altair.app.ticketing.core.models import (
        Organization,
        Event,
        Performance,
        )
    organization = None
    event = None
    performance = None
    if args.organization:
        organization = session.query(Organization) \
            .filter(sql.or_(
                Organization.id == args.organization,
                Organization.name == args.organization,
                Organization.short_name == args.organization,
                )) \
            .one()
    if args.event:
        q = session.query(Event) \
            .filter(sql.or_(
                Event.id == args.event,
                Event.title == args.event,
                Event.code == args.event,
                ))
        if organization:
            q = q.filter(Event.organization_id == organization.id)
        event = q.one()
    if args.performance:
        q = session.query(Performance) \
            .filter(sql.or_(
                Performance.id == args.performance,
                Performance.name == args.performance,
                Performance.code == args.performance,
                ))
        if event:
            q = q.filter(Performance.event_id == event.id)
        performance = q.one()
    if args.mode == 'import':
        do_import(request, session, organization, event, performance, args.order_no)
    elif args.mode == 'export':
        do_export(request, session, organization, event, performance, args.order_no)

    return 0 

if __name__ == '__main__':
    sys.exit(main(sys.argv))
