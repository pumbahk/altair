# coding=utf-8
from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
from altair.app.ticketing.core.models import (
    Organization, OrganizationSetting, Performance, Event, EventSetting,
    Product, ProductItem, Stock, StockType, Seat, SalesSegment, SalesSegmentGroup, SiteProfile, Site, Venue)
from altair.app.ticketing.skidata.models import (
    SkidataBarcode, SkidataProperty, SkidataPropertyTypeEnum, SkidataPropertyEntry)


def create_organization(session, code, short_name, enable_skidata):
    organization = Organization(code=code, short_name=short_name)
    session.add(organization)

    organization_setting = OrganizationSetting(organization=organization, enable_skidata=enable_skidata)
    session.add(organization_setting)
    return organization


def create_event(session, organization, title, enable_skidata):
    event_setting = EventSetting(enable_skidata=enable_skidata)
    session.add(event_setting)

    event = Event(
        title=title,
        organization=organization,
        setting=event_setting,
    )
    session.add(event)
    return event


def create_performance(session, event, name, open_on, start_on):
    performance = Performance(
        name=name,
        open_on=open_on,
        start_on=start_on,
        event=event
    )
    session.add(performance)
    return performance


def create_stock(session, event, performance, name):
    stock_type = StockType(
        name=name,
        event=event,
        attribute=u'Gate A'
    )
    session.add(stock_type)

    stock = Stock(
        performance=performance,
        stock_type=stock_type
    )
    session.add(stock)
    return stock


def create_sales_segment(session, organization, event, performance):
    sales_segment_group = SalesSegmentGroup(
        name=u'一般発売',
        event=event,
        organization=organization
    )
    session.add(sales_segment_group)

    sales_segment = SalesSegment(
        performance=performance,
        sales_segment_group=sales_segment_group,
        event=event
    )
    session.add(sales_segment)
    return sales_segment


def create_product_info(session, performance, stock, sales_segment, product_name):
    product = Product(
        name=product_name,
        price=3000,
        sales_segment=sales_segment,
        performance=performance
    )
    session.add(product)

    product_item = ProductItem(
        product=product,
        price=3000,
        performance=performance,
        stock=stock
    )
    session.add(product_item)
    return product, product_item


def create_venue(session, organization, performance, name, prefecture):
    siteprofile = SiteProfile(name=name, prefecture=prefecture)
    session.add(siteprofile)

    site = Site(siteprofile=siteprofile, name=name, prefecture=prefecture)
    session.add(site)

    venue = Venue(site=site, performance=performance, organization=organization, name=name)
    session.add(venue)
    return venue


def create_order_info(session, organization_id, performance, product, product_item, order_no, paid_at):
    order = Order(
        order_no=order_no,
        total_amount=6000,
        system_fee=0,
        transaction_fee=0,
        delivery_fee=0,
        organization_id=organization_id,
        performance=performance,
        paid_at=paid_at
    )
    session.add(order)

    ordered_product = OrderedProduct(
        order=order,
        product=product,
        price=3000,
        refund_price=0
    )
    session.add(ordered_product)

    ordered_product_item = OrderedProductItem(
        ordered_product=ordered_product,
        product_item=product_item,
        price=3000,
        refund_price=0,
        quantity=2
    )
    session.add(ordered_product_item)
    return ordered_product_item


def create_barcode_recorder(session, stock, venue, ordered_product_item, seat_name, data):
    seat = Seat(name=seat_name, stock=stock, venue=venue)
    session.add(seat)

    ordered_product_item_token = OrderedProductItemToken(
        item=ordered_product_item,
        seat=seat,
        serial=0,
    )
    session.add(ordered_product_item_token)

    skidata_barcode = SkidataBarcode(
        ordered_product_item_token=ordered_product_item_token,
        data=data
    )
    session.add(skidata_barcode)
    return skidata_barcode