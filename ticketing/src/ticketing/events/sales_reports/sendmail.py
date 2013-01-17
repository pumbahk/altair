# -*- coding: utf-8 -*-

from pyramid.threadlocal import get_current_registry
from sqlalchemy.sql import func
from ticketing.operators.models import Operator
from ticketing.core.models import Event, Organization, ReportSetting, Mailer
from ticketing.core.models import StockType, StockHolder, StockStatus, Stock, Performance, Product, ProductItem, SalesSegment
from ticketing.core.models import Order, OrderedProduct, OrderedProductItem
from ticketing.events.sales_reports.forms import SalesReportForm
from pyramid.renderers import render_to_response
import logging

logger = logging.getLogger(__name__)

def get_sales_summary(form, organization, group='Event'):
    reports = {}

    # 自社分のみが対象
    stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=organization.user_id)]

    # 配席数、在庫数
    query = Event.query.filter(Event.organization_id==organization.id)\
        .outerjoin(Performance).filter(Performance.deleted_at==None)\
        .outerjoin(Stock).filter(Stock.deleted_at==None, Stock.stock_holder_id.in_(stock_holder_ids))\
        .outerjoin(StockStatus).filter(StockStatus.deleted_at==None)
    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)
    event_start_day = func.min(Performance.start_on.label('performance_start_on'))
    event_end_day = func.max(Performance.end_on.label('performance_end_on'))

    if group == 'Performance':
        query = query.with_entities(
            Performance.id,
            Performance.name,
            Performance.start_on,
            func.sum(Stock.quantity),
            func.sum(StockStatus.quantity),
            event_start_day,
            event_end_day,
        ).group_by(Performance.id)
    else:
        query = query.with_entities(
            Event.id,
            Event.title,
            Event.id, # dummy
            func.sum(Stock.quantity),
            func.sum(StockStatus.quantity),
            event_start_day,
            event_end_day,
        ).group_by(Event.id)

    for id, title, start_on, total_quantity, vacant_quantity, event_start_day, event_end_day in query.all():
        reports[id] = dict(
            id=id,
            title=title,
            start_on=start_on,
            total_quantity=total_quantity or 0,
            vacant_quantity=vacant_quantity or 0,
            total_amount=0,
            fee_amount=0,
            price_amount=0,
            product_quantity=0,
            event_start_day=event_start_day,
            event_end_day=event_end_day,
        )

    # 販売金額、販売枚数
    query = Event.query.filter(Event.organization_id==organization.id)\
        .outerjoin(Performance).filter(Performance.deleted_at==None)\
        .outerjoin(Order).filter(Order.canceled_at==None, Order.deleted_at==None)\
        .outerjoin(OrderedProduct).filter(OrderedProduct.deleted_at==None)
    if form.limited_from.data:
        query = query.filter(Order.created_at > form.limited_from.data)
    if form.limited_to.data:
        query = query.filter(Order.created_at < form.limited_to.data)
    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)

    if group == 'Performance':
        query = query.with_entities(
            Performance.id,
            func.sum(OrderedProduct.price * OrderedProduct.quantity).label('price_amount'),
            func.sum(OrderedProduct.quantity).label('product_quantity')
        ).group_by(Performance.id)
    else:
        query = query.with_entities(
            Event.id,
            func.sum(OrderedProduct.price * OrderedProduct.quantity).label('price_amount'),
            func.sum(OrderedProduct.quantity).label('product_quantity')
        ).group_by(Event.id)

    for id, price_amount, product_quantity in query.all():
        if id in reports:
            reports[id].update(dict(price_amount=price_amount or 0, product_quantity=product_quantity or 0))

    return reports.values()

def get_performance_sales_summary(form, organization):
    performance_reports = {}

    # in-house
    stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=organization.user_id)]

    # about product, seats, stocks
    query = StockType.query.filter(StockType.id==Stock.stock_type_id)\
        .outerjoin(Stock).filter(Stock.id==ProductItem.stock_id, Stock.stock_holder_id.in_(stock_holder_ids))\
        .outerjoin(StockHolder).filter(StockHolder.id==Stock.stock_holder_id)\
        .outerjoin(StockStatus).filter(StockStatus.stock_id==Stock.id)\
        .outerjoin(Product).filter(Product.seat_stock_type_id==StockType.id)
    if form.event_id.data:
        query = query.filter(Product.event_id==form.event_id.data)
        query = query.outerjoin(ProductItem).filter(ProductItem.product_id==Product.id)
        total_quantity_entity = func.sum(Stock.quantity).label('total_quantity')
        stock_quantity_entity = func.sum(StockStatus.quantity).label('vacant_quantity')
    else:
        total_quantity_entity = Stock.quantity.label('total_quantity')
        stock_quantity_entity = StockStatus.quantity.label('vacant_quantity')
    if form.performance_id.data:
        query = query.outerjoin(ProductItem).filter(ProductItem.product_id==Product.id, ProductItem.performance_id==form.performance_id.data)
    if form.sales_segment_id.data:
        query = query.outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)
        sales_segment_name_entity = SalesSegment.name.label('sales_segment_name')
    else:
        sales_segment_name_entity = 'NULL'

    query = query.with_entities(
            StockType.id.label('stock_type_id'),
            StockType.name.label('stock_type_name'),
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            Product.price.label('product_price'),
            total_quantity_entity,
            stock_quantity_entity,
            StockHolder.id.label('stock_holder_id'),
            StockHolder.name.label('stock_holder_name'),
            sales_segment_name_entity,
            Stock.id.label('stock_id'),
        )
    if form.event_id.data:
        query = query.group_by(Product.id)

    for row in query.all():
        performance_reports[row[2]] = dict(
            stock_id=row[10],
            stock_type_id=row[0],
            stock_type_name=row[1],
            product_id=row[2],
            product_name=row[3],
            product_price=row[4],
            total_quantity=row[5] or 0,
            vacant_quantity=row[6] or 0,
            stock_holder_id=row[7],
            stock_holder_name=row[8],
            sales_segment_name=row[9],
            order_quantity=0,
            paid_quantity=0,
            unpaid_quantity=0,
        )

    # paid
    query = OrderedProduct.query.join(Order)\
        .filter(Order.canceled_at==None, Order.paid_at!=None)\
        .outerjoin(Product).filter(Product.id==OrderedProduct.product_id)
    if form.event_id.data:
        query = query.filter(Product.event_id==form.event_id.data)
    if form.performance_id.data:
        query = query.filter(Order.performance_id==form.performance_id.data)
    if form.sales_segment_id.data:
        query = query.outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)
    if form.limited_from.data:
        query = query.filter(Order.created_at > form.limited_from.data)
    if form.limited_to.data:
        query = query.filter(Order.created_at < form.limited_to.data)
    
    query = query.with_entities(
            OrderedProduct.product_id,
            func.sum(OrderedProduct.quantity).label('ordered_product_quantity')
        )
    query = query.group_by(OrderedProduct.product_id)

    for id, paid_quantity in query.all():
        if id not in performance_reports:
            logger.warn('invalid key (product_id:%s)' % id)
            continue
        performance_reports[id].update(dict(paid_quantity=paid_quantity or 0))

    # unpaid
    query = OrderedProduct.query.join(Order)\
        .filter(Order.canceled_at==None, Order.paid_at==None)\
        .outerjoin(Product).filter(Product.id==OrderedProduct.product_id)
    if form.event_id.data:
        query = query.filter(Product.event_id==form.event_id.data)
    if form.performance_id.data:
        query = query.filter(Order.performance_id==form.performance_id.data)
    if form.sales_segment_id.data:
        query = query.outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)
    if form.limited_from.data:
        query = query.filter(Order.created_at > form.limited_from.data)
    if form.limited_to.data:
        query = query.filter(Order.created_at < form.limited_to.data)
    
    query = query.with_entities(
            OrderedProduct.product_id,
            func.sum(OrderedProduct.quantity).label('ordered_product_quantity')
        )
    query = query.group_by(OrderedProduct.product_id)

    for id, unpaid_quantity in query.all():
        if id not in performance_reports:
            logger.warn('invalid key (product_id:%s)' % id)
            continue
        performance_reports[id].update(dict(unpaid_quantity=unpaid_quantity or 0))

    return performance_reports.values()

def sendmail(event, form=None):
    performances_reports = {}
    for performance in event.performances:
        report_by_sales_segment = {}
        for sales_segment in event.sales_segments:
            sales_report_form = form or SalesReportForm(form.data, performance_id=performance.id, sales_segment_id=sales_segment.id)
            report_by_sales_segment[sales_segment.name] = get_performance_sales_summary(sales_report_form, event.organization)
        performances_reports[performance.id] = dict(
            performance=performance,
            report_by_sales_segment=report_by_sales_segment
        )

    render_param = {
        'event_product':get_performance_sales_summary(form, event.organization),
        'form':form,
        'performances_reports':performances_reports
    }

    registry = get_current_registry()
    settings = registry.settings

    sender = settings['mail.message.sender']
    recipient = form.recipient.data
    html = render_to_response('ticketing:templates/sales_reports/mail_body.html', render_param, request=None)
    mailer = Mailer(settings)
    mailer.create_message(
        sender = sender,
        recipient = recipient,
        subject = u'[売上レポート] %s' % event.title,
        body = '',
        html = html.text
    ) 
    try:
        mailer.send(sender, recipient.split(','))
    except Exception, e:
        logging.error(e.message)
