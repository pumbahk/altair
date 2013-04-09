# -*- coding: utf-8 -*-

import logging

from paste.util.multidict import MultiDict
from pyramid.threadlocal import get_current_registry
from pyramid.renderers import render_to_response
from sqlalchemy import distinct
from sqlalchemy.sql import func, and_, or_

from ticketing.core.models import Event, Mailer
from ticketing.core.models import StockType, StockHolder, StockStatus, Stock, Performance, Product, ProductItem, SalesSegmentGroup, SalesSegment
from ticketing.core.models import Order, OrderedProduct
from ticketing.events.sales_reports.forms import SalesReportForm
from ticketing.helpers import todatetime

logger = logging.getLogger(__name__)

def get_sales_summary(form, organization, group='Event'):
    '''
    イベント毎、または公演毎に集計したレポートを返す
    :param form: SalesReportForm
    :param organization: Organization
    :param group: 集計単位  'Event' イベント毎の集計、'Performance' 公演毎の集計
    :return:
        [{'id': イベントID / 公演ID,
          'title': イベント名称 / 公演名称,
          'start_on': 公演開始日,
          'total_quantity': 配席数,
          'vacant_quantity': 残席数,
          'product_quantity': 販売枚数合計,
          'price_amount': 販売金額合計,
          'sales_start_day': 販売開始日,
          'sales_end_day': 販売終了日},
          {...},
        ]
    '''
    reports = {}

    # 自社分のみが対象
    stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=organization.user_id)]

    # 名称、期間
    query = Event.query.filter(Event.organization_id==organization.id)\
        .outerjoin(Performance).filter(Performance.deleted_at==None)\
        .outerjoin(Stock).filter(Stock.deleted_at==None, Stock.stock_holder_id.in_(stock_holder_ids))\
        .outerjoin(StockStatus).filter(StockStatus.deleted_at==None)\
        .outerjoin(SalesSegment, SalesSegment.performance_id==Performance.id).filter(SalesSegment.public==True)

    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)

    if group == 'Performance':
        group_key = Performance.id
        name = Performance.name
        start_on = Performance.start_on
    else:
        group_key = Event.id
        name = Event.title
        start_on = Event.id  # dummy
    query = query.with_entities(
        group_key,
        name,
        start_on,
        func.min(SalesSegment.start_at.label('sales_start_at')),
        func.max(SalesSegment.end_at.label('sales_end_at')),
    ).group_by(group_key)

    for id, title, start_on, sales_start_day, sales_end_day in query.all():
        reports[id] = dict(
            id=id,
            title=title,
            start_on=start_on,
            total_quantity=0,
            vacant_quantity=0,
            price_amount=0,
            product_quantity=0,
            sales_start_day=sales_start_day,
            sales_end_day=sales_end_day,
        )

    # 配席数、残席数
    query = Stock.query.filter(Stock.stock_holder_id.in_(stock_holder_ids))\
        .join(StockStatus)\
        .join(ProductItem)\
        .join(Product).filter(Product.seat_stock_type_id==Stock.stock_type_id)\
        .join(Performance).filter(Performance.id==Stock.performance_id)\
        .join(Event).filter(Event.organization_id==organization.id)\
        .join(SalesSegment, SalesSegment.performance_id==Performance.id).filter(SalesSegment.public==True)

    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)
    stock_ids = [s.id for s in query.with_entities(Stock.id).distinct()]

    query = Stock.query.filter(Stock.id.in_(stock_ids))\
        .join(StockStatus)\
        .join(Performance).filter(Performance.id==Stock.performance_id)\
        .join(Event).filter(Event.organization_id==organization.id)

    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)

    query = query.with_entities(
        group_key,
        func.sum(Stock.quantity),
        func.sum(StockStatus.quantity)
    ).group_by(group_key)

    for id, total_quantity, vacant_quantity in query.all():
        if id in reports:
            reports[id].update(dict(total_quantity=total_quantity or 0, vacant_quantity=vacant_quantity or 0))

    # 販売金額、販売枚数
    query = Event.query.filter(Event.organization_id==organization.id)\
        .outerjoin(Performance).filter(Performance.deleted_at==None)\
        .outerjoin(Order).filter(Order.canceled_at==None, Order.deleted_at==None)\
        .outerjoin(OrderedProduct).filter(OrderedProduct.deleted_at==None)\
        .outerjoin(Product).filter(Product.deleted_at==None)\
        .outerjoin(SalesSegment).filter(or_(SalesSegment.performance_id==None, SalesSegment.public==True))

    if form.limited_from.data:
        query = query.filter(Order.created_at >= form.limited_from.data)
    if form.limited_to.data:
        query = query.filter(Order.created_at < form.limited_to.data)
    if form.performance_id.data:
        query = query.filter(Performance.id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(Event.id==form.event_id.data)

    query = query.with_entities(
        group_key,
        func.sum(OrderedProduct.price * OrderedProduct.quantity).label('price_amount'),
        func.sum(OrderedProduct.quantity).label('product_quantity')
    ).group_by(group_key)

    for id, price_amount, product_quantity in query.all():
        if id in reports:
            reports[id].update(dict(price_amount=price_amount or 0, product_quantity=product_quantity or 0))

    return reports.values()

def get_performance_sales_summary(form, organization):
    '''
    公演の販売区分毎、席種毎、商品毎に集計したレポートを返す
    :param form: SalesReportForm
    :param organization: Organization
    :return: unique keyは product_id
        [{'stock_type_id': 席種ID,
          'stock_type_name': 席種名,
          'product_id': 商品ID,
          'product_name': 商品名,
          'product_price': 商品単価,
          'stock_holder_id': 枠ID,
          'stock_holder_name': 枠名,
          'sales_segment_group_name': 販売区分名,
          'stock_id': 在庫ID,
          'total_quantity': 配席数,
          'vacant_quantity': 残数,
          'paid_quantity': 入金済み,
          'unpaid_quantity': 未入金},
          {...},
        ]
    '''
    performance_reports = {}

    # 自社分のみが対象
    if form.performance_id.data:
        performance = Performance.get(form.performance_id.data)
        event = performance.event
    elif form.event_id.data:
        event = Event.get(form.event_id.data)
    else:
        logger.error('event_id not found')
        return
    stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(event=event)]

    # 名称、期間
    query = StockType.query\
        .outerjoin(Stock).filter(Stock.stock_holder_id.in_(stock_holder_ids))\
        .outerjoin(StockHolder)\
        .outerjoin(StockStatus)\
        .outerjoin(ProductItem)\
        .outerjoin(Product).filter(Product.seat_stock_type_id==Stock.stock_type_id)

    if form.performance_id.data:
        query = query.filter(ProductItem.performance_id==form.performance_id.data)
    if form.event_id.data:
        query = query.filter(StockType.event_id==form.event_id.data)
    if form.sales_segment_group_id.data:
        query = query.join(SalesSegment).filter(or_(SalesSegment.performance_id==None, SalesSegment.public==True))
        query = query.join(SalesSegmentGroup).filter(
            SalesSegmentGroup.id==form.sales_segment_group_id.data,
        )
        sales_segment_group_name_entity = SalesSegmentGroup.name.label('sales_segment_group_name')
    else:
        sales_segment_group_name_entity = 'NULL'

    query = query.with_entities(
        StockType.id.label('stock_type_id'),
        StockType.name.label('stock_type_name'),
        func.ifnull(Product.base_product_id, Product.id).label('product_id'),
        Product.name.label('product_name'),
        Product.price.label('product_price'),
        StockHolder.id.label('stock_holder_id'),
        StockHolder.name.label('stock_holder_name'),
        sales_segment_group_name_entity,
        Stock.id.label('stock_id'),
    ).group_by(func.ifnull(Product.base_product_id, Product.id))

    for row in query.all():
        performance_reports[row[2]] = dict(
            stock_type_id=row[0],
            stock_type_name=row[1],
            product_id=row[2],
            product_name=row[3],
            product_price=row[4],
            stock_holder_id=row[5],
            stock_holder_name=row[6],
            sales_segment_group_name=row[7],
            stock_id=row[8],
            total_quantity=0,
            vacant_quantity=0,
            paid_quantity=0,
            unpaid_quantity=0,
        )

    # 配席数、残席数
    query = Stock.query.filter(Stock.stock_holder_id.in_(stock_holder_ids))\
        .join(StockStatus).filter(StockStatus.deleted_at==None)\
        .join(ProductItem).filter(ProductItem.deleted_at==None)\
        .join(Product).filter(and_(Product.seat_stock_type_id==Stock.stock_type_id, Product.base_product_id==None))

    if form.performance_id.data:
        query = query.filter(Stock.performance_id==form.performance_id.data)
    if form.event_id.data:
        query = query.join(StockType).filter(StockType.event_id==form.event_id.data)
    if form.sales_segment_group_id.data:
        query = query.join(SalesSegment).filter(or_(SalesSegment.performance_id==None, SalesSegment.public==True))
        query = query.join(SalesSegmentGroup).filter(
            SalesSegmentGroup.id==form.sales_segment_group_id.data,
        )
    query = query.with_entities(
        func.ifnull(Product.base_product_id, Product.id),
        func.sum(Stock.quantity),
        func.sum(StockStatus.quantity)
    ).group_by(func.ifnull(Product.base_product_id, Product.id))

    for id, total_quantity, vacant_quantity in query.all():
        if id not in performance_reports:
            logger.warn('invalid key (product_id:%s) total_quantity query' % id)
            continue
        performance_reports[id].update(dict(total_quantity=total_quantity or 0, vacant_quantity=vacant_quantity or 0))

    # 購入件数クエリ
    query = OrderedProduct.query\
        .join(Order).filter(Order.canceled_at==None)\
        .join(Product).filter(Product.id==OrderedProduct.product_id)
    if form.performance_id.data:
        query = query.filter(Order.performance_id==form.performance_id.data)
    elif form.event_id.data:
        query = query.join(StockType).filter(StockType.event_id==form.event_id.data)
    if form.sales_segment_group_id.data:
        query = query.join(SalesSegment).filter(or_(SalesSegment.performance_id==None, SalesSegment.public==True))
        query = query.join(SalesSegmentGroup).filter(
            SalesSegmentGroup.id==form.sales_segment_group_id.data
        )
    if form.limited_from.data:
        query = query.filter(Order.created_at >= form.limited_from.data)
    if form.limited_to.data:
        query = query.filter(Order.created_at < form.limited_to.data)

    # 入金済み
    paid_query = query.filter(Order.paid_at!=None)
    paid_query = paid_query.with_entities(
        func.ifnull(Product.base_product_id, Product.id),
        func.sum(OrderedProduct.quantity).label('ordered_product_quantity')
    ).group_by(func.ifnull(Product.base_product_id, Product.id))

    for id, paid_quantity in paid_query.all():
        if id not in performance_reports:
            logger.warn('invalid key (product_id:%s) paid_quantity query' % id)
            continue
        performance_reports[id]['paid_quantity'] += paid_quantity

    # 未入金
    unpaid_query = query.filter(Order.paid_at==None)
    unpaid_query = unpaid_query.with_entities(
        func.ifnull(Product.base_product_id, Product.id),
        func.sum(OrderedProduct.quantity).label('ordered_product_quantity')
    ).group_by(func.ifnull(Product.base_product_id, Product.id))

    for id, unpaid_quantity in unpaid_query.all():
        if id not in performance_reports:
            logger.warn('invalid key (product_id:%s) unpaid_quantity query' % id)
            continue
        performance_reports[id]['unpaid_quantity'] += unpaid_quantity

    return performance_reports.values()

def get_performance_sales_detail(form, event):
    performances_reports = {}
    for performance in event.performances:
        report_by_sales_segment_group = {}
        if form.limited_from.data is None or performance.end_on is None or form.limited_from.data < performance.end_on:
            for sales_segment in performance.sales_segments:
                if not sales_segment.public:
                    continue
                if (form.limited_from.data is None or todatetime(form.limited_from.data) < sales_segment.end_at) or\
                   (form.limited_to.data is None or sales_segment.start_at <= todatetime(form.limited_to.data)):
                    form.performance_id.data = performance.id
                    form.sales_segment_group_id.data = sales_segment.sales_segment_group_id
                    report_by_sales_segment_group[sales_segment] = get_performance_sales_summary(form, event.organization)
        performances_reports[performance] = report_by_sales_segment_group
    return performances_reports

def sendmail(event, form=None):
    render_param = {
        'event_product':get_performance_sales_summary(form, event.organization),
        'event_product_total':get_performance_sales_summary(SalesReportForm(event_id=event.id), event.organization),
        'form':form,
        'performances_reports':get_performance_sales_detail(form, event),
        'performances_reports_total':get_performance_sales_detail(SalesReportForm(event_id=event.id), event)
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
