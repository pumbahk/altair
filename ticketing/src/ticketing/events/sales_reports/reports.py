# -*- coding: utf-8 -*-

import logging

from paste.util.multidict import MultiDict
from pyramid.threadlocal import get_current_registry
from pyramid.renderers import render_to_response
from sqlalchemy import distinct
from sqlalchemy.sql import func, and_, or_
from sqlalchemy.orm import aliased

from ticketing.core.models import Event, Mailer
from ticketing.core.models import StockType, StockHolder, StockStatus, Stock, Performance, Product, ProductItem, SalesSegmentGroup, SalesSegment
from ticketing.core.models import Order, OrderedProduct
from ticketing.helpers import todatetime

logger = logging.getLogger(__name__)


class SalesReportRecord(object):

    def __init__(self, id, title, start_on, sales_start_day, sales_end_day):
        # イベントID / 公演ID
        self.id = id
        # イベント名称 / 公演名称
        self.title = title
        # 公演開始日
        self.start_on = start_on
        # 販売開始日
        self.sales_start_day = sales_start_day
        # 販売終了日
        self.sales_end_day = sales_end_day
        # 配席数
        self.stock_quantity = 0
        # 残席数
        self.vacant_quantity = 0
        # 販売枚数合計
        self.order_quantity = 0
        # 販売金額合計
        self.order_amount = 0
        # 販売枚数合計(全期間)
        self.total_order_quantity = 0
        # 販売金額合計(全期間)
        self.total_order_amount = 0


class SalesTotalReporter(object):

    def __init__(self, form, organization, group_by='Event'):
        '''
        イベント毎、または公演毎に集計したレポート
        :param form: SalesReportForm
        :param organization: Organization
        :param group: 集計単位  'Event' イベント毎の集計、'Performance' 公演毎の集計
        '''
        self.form = form
        self.organization = organization
        self.group_by = Performance.id if group_by == 'Performance' else Event.id
        self.reports = {}
        self.stock_holder_ids = []

        # レポートデータ生成
        self.create_reports()

    def create_reports(self):
        # 自社分のみが対象
        self.stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=self.organization.user_id)]
        self.get_event_data()
        self.get_stock_data()
        self.get_order_data()

    def add_form_filter(self, query):
        query = query.filter(Performance.public==True)
        if self.form.performance_id.data:
            query = query.filter(Performance.id==self.form.performance_id.data)
        if self.form.event_id.data:
            query = query.filter(Event.id==self.form.event_id.data)
        return query

    def add_sales_segment_filter(self, query):
        # performance_idがないSalesSegmentは[SalesSegmentGroupのデータ移行以前のレコード]なので、publicがFalseでも含める
        # ただし、対象performance_idのSalesSegment.publicがTrueであること
        ss = aliased(SalesSegment, name='SalesSegment_alias')
        query = query.join(SalesSegment, SalesSegment.id==Product.sales_segment_id).filter(
            or_(SalesSegment.performance_id==None, SalesSegment.public==True)
        )
        query = query.outerjoin(ss, and_(
            ss.sales_segment_group_id==SalesSegment.sales_segment_group_id,
            ss.performance_id==Performance.id,
            ss.deleted_at==None
        )).filter(or_(SalesSegment.public==True, ss.public==True))
        return query

    def get_event_data(self):
        # イベント名称/公演名称、販売期間
        # 一般公開されている販売区分のみ対象
        query = Event.query.filter(Event.organization_id==self.organization.id)\
            .outerjoin(Performance).filter(Performance.deleted_at==None)\
            .outerjoin(Stock).filter(Stock.deleted_at==None, Stock.stock_holder_id.in_(self.stock_holder_ids))\
            .outerjoin(StockStatus).filter(StockStatus.deleted_at==None)\
            .outerjoin(SalesSegment, SalesSegment.performance_id==Performance.id).filter(SalesSegment.public==True)
        query = self.add_form_filter(query)

        if self.group_by == Performance.id:
            name = Performance.name
            start_on = Performance.start_on
        else:
            name = Event.title
            start_on = Event.id  # dummy
        query = query.with_entities(
            self.group_by,
            name,
            start_on,
            func.min(SalesSegment.start_at),
            func.max(SalesSegment.end_at),
        ).group_by(self.group_by)

        for id, title, start_on, sales_start_day, sales_end_day in query.all():
            self.reports[id] = SalesReportRecord(
                id=id,
                title=title,
                start_on=start_on,
                sales_start_day=sales_start_day,
                sales_end_day=sales_end_day,
            )

    def get_stock_data(self):
        # 配席数、残席数
        query = Stock.query.filter(Stock.stock_holder_id.in_(self.stock_holder_ids))\
            .join(StockStatus).filter(StockStatus.deleted_at==None)\
            .join(ProductItem).filter(ProductItem.deleted_at==None)\
            .join(Product).filter(Product.seat_stock_type_id==Stock.stock_type_id)\
            .join(Performance).filter(Performance.id==Stock.performance_id)\
            .join(Event).filter(Event.organization_id==self.organization.id)
        query = self.add_sales_segment_filter(query)
        query = self.add_form_filter(query)
        stock_ids = [s.id for s in query.with_entities(Stock.id).distinct()]

        query = Stock.query.filter(Stock.id.in_(stock_ids))\
            .join(StockStatus)\
            .join(Performance).filter(Performance.id==Stock.performance_id)\
            .join(Event).filter(Event.organization_id==self.organization.id)
        query = self.add_form_filter(query)
        query = query.with_entities(
            self.group_by,
            func.sum(Stock.quantity),
            func.sum(StockStatus.quantity)
        ).group_by(self.group_by)

        for id, stock_quantity, vacant_quantity in query.all():
            if id not in self.reports:
                logger.warn('invalid key (%s:%s) get_stock_data' % (self.group_by, id))
                continue
            record = self.reports[id]
            record.stock_quantity = stock_quantity or 0
            record.vacant_quantity = vacant_quantity or 0

    def get_order_data(self):
        # 販売金額、販売枚数
        query = Event.query.filter(Event.organization_id==self.organization.id)\
            .outerjoin(Performance).filter(Performance.deleted_at==None)\
            .outerjoin(Order).filter(Order.canceled_at==None, Order.deleted_at==None)\
            .outerjoin(OrderedProduct).filter(OrderedProduct.deleted_at==None)\
            .outerjoin(Product).filter(Product.deleted_at==None)
        query = self.add_sales_segment_filter(query)
        query = self.add_form_filter(query)
        query = query.with_entities(
            self.group_by,
            func.sum(OrderedProduct.price * OrderedProduct.quantity),
            func.sum(OrderedProduct.quantity)
        ).group_by(self.group_by)

        for id, order_amount, order_quantity in query.all():
            if id not in self.reports:
                logger.warn('invalid key (%s:%s) get_order_data' % (self.group_by, id))
                continue
            record = self.reports[id]
            record.total_order_amount = order_amount or 0
            record.total_order_quantity = order_quantity or 0

        # 販売金額(期間指定)、販売枚数(期間指定)
        if self.form.limited_from.data or self.form.limited_to.data:
            if self.form.limited_from.data:
                query = query.filter(Order.created_at >= self.form.limited_from.data)
            if self.form.limited_to.data:
                query = query.filter(Order.created_at < self.form.limited_to.data)
            for id, order_amount, order_quantity in query.all():
                if id not in self.reports:
                    logger.warn('invalid key (%s:%s) get_order_data' % (self.group_by, id))
                    continue
                record = self.reports[id]
                record.order_amount = order_amount or 0
                record.order_quantity = order_quantity or 0
        else:
            for record in self.reports.values():
                record.order_amount = record.total_order_amount
                record.order_quantity = record.total_order_quantity

    def sort_data(self):
        return sorted(self.reports.values(), key=lambda x:(x.start_on, x.title))

    def pop_data(self):
        return self.reports.values().pop()


class SalesDetailReportRecord(object):

    def __init__(self, stock_type_id=None,
                 stock_type_name=None,
                 product_id=None,
                 product_name=None,
                 product_price=None,
                 stock_holder_id=None,
                 stock_holder_name=None,
                 sales_segment_group_name=None,
                 stock_id=None):
        # 席種ID
        self.stock_type_id = stock_type_id
        # 席種名
        self.stock_type_name = stock_type_name
        # 商品ID
        self.product_id = product_id
        # 商品名
        self.product_name = product_name
        # 商品単価
        self.product_price = product_price
        # 枠ID
        self.stock_holder_id = stock_holder_id
        # 枠名
        self.stock_holder_name = stock_holder_name
        # 販売区分名
        self.sales_segment_group_name = sales_segment_group_name
        # 在庫ID
        self.stock_id = stock_id
        # 配席数
        self.stock_quantity = 0
        # 残数
        self.vacant_quantity = 0
        # 入金済み
        self.paid_quantity = 0
        # 未入金
        self.unpaid_quantity = 0
        # 小計
        self.sum_amount = 0
        # 入金済み(全期間)
        self.total_paid_quantity = 0
        # 未入金(全期間)
        self.total_unpaid_quantity = 0
        # 小計(全期間)
        self.total_sum_amount = 0

    def group_key(self):
        return self.stock_id


class SalesDetailReporter(object):

    def __init__(self, form):
        '''
        公演の販売区分毎、席種毎、商品毎に集計したレポートを返す
        :param form: SalesReportForm
        '''
        self.form = form
        self.reports = {}
        self.total = None

        # レポートデータ生成
        self.create_reports()

    def create_reports(self):
        # 自社分のみが対象
        if self.form.performance_id.data:
            performance = Performance.get(self.form.performance_id.data)
            event = performance.event
        elif self.form.event_id.data:
            event = Event.get(self.form.event_id.data)
        else:
            logger.error('event_id not found')
            return
        self.stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(event=event)]
        self.get_performance_data()
        self.get_stock_data()
        self.get_order_data()
        if self.form.limited_from.data or self.form.limited_to.data:
            self.get_order_data(all_period=False)
        self.create_group_key_to_reports()
        self.calculate_total()

    def add_sales_segment_filter(self, query):
        # performance_idがないSalesSegmentは[SalesSegmentGroupのデータ移行以前のレコード]なので、publicがFalseでも含める
        # ただし、対象performance_idのSalesSegment.publicがTrueであること
        query = query.join(SalesSegment, SalesSegment.id==Product.sales_segment_id).filter(
            or_(SalesSegment.performance_id==None, SalesSegment.public==True)
        )
        if self.form.sales_segment_group_id.data:
            query = query.join(SalesSegmentGroup).filter(and_(
                SalesSegmentGroup.id==self.form.sales_segment_group_id.data,
                SalesSegmentGroup.deleted_at==None
            ))
        if self.form.performance_id.data:
            ss = aliased(SalesSegment, name='SalesSegment_alias')
            query = query.outerjoin(ss, and_(
                ss.sales_segment_group_id==SalesSegment.sales_segment_group_id,
                ss.performance_id==self.form.performance_id.data,
                ss.deleted_at==None
            )).filter(or_(SalesSegment.public==True, ss.public==True))
        return query

    def get_performance_data(self):
        # 名称、期間
        query = StockType.query\
            .outerjoin(Stock).filter(Stock.stock_holder_id.in_(self.stock_holder_ids))\
            .outerjoin(StockHolder)\
            .outerjoin(StockStatus)\
            .outerjoin(ProductItem)\
            .outerjoin(Product).filter(Product.seat_stock_type_id==Stock.stock_type_id)
        query = self.add_sales_segment_filter(query)
        if self.form.performance_id.data:
            query = query.filter(ProductItem.performance_id==self.form.performance_id.data)
        if self.form.event_id.data:
            query = query.filter(StockType.event_id==self.form.event_id.data)

        query = query.with_entities(
            func.ifnull(Product.base_product_id, Product.id),
            StockType.id,
            StockType.name,
            Product.name,
            Product.price,
            StockHolder.id,
            StockHolder.name,
            SalesSegmentGroup.name if self.form.sales_segment_group_id.data else 'NULL',
            Stock.id,
        ).group_by(func.ifnull(Product.base_product_id, Product.id))

        for row in query.all():
            self.reports[row[0]] = SalesDetailReportRecord(
                stock_type_id=row[1],
                stock_type_name=row[2],
                product_id=row[0],
                product_name=row[3],
                product_price=row[4],
                stock_holder_id=row[5],
                stock_holder_name=row[6],
                sales_segment_group_name=row[7],
                stock_id=row[8]
            )

    def get_stock_data(self):
        # 配席数、残席数
        query = Stock.query.filter(Stock.stock_holder_id.in_(self.stock_holder_ids))\
            .join(StockStatus).filter(StockStatus.deleted_at==None)\
            .join(ProductItem).filter(ProductItem.deleted_at==None)\
            .join(Product).filter(and_(Product.seat_stock_type_id==Stock.stock_type_id, Product.base_product_id==None))
        query = self.add_sales_segment_filter(query)
        if self.form.performance_id.data:
            query = query.filter(Stock.performance_id==self.form.performance_id.data)
        if self.form.event_id.data:
            query = query.join(StockType, StockType.id==Stock.stock_type_id).filter(StockType.event_id==self.form.event_id.data)

        query = query.with_entities(
            func.ifnull(Product.base_product_id, Product.id),
            func.sum(Stock.quantity),
            func.sum(StockStatus.quantity)
        ).group_by(func.ifnull(Product.base_product_id, Product.id))

        for id, stock_quantity, vacant_quantity in query.all():
            if id not in self.reports:
                logger.warn('invalid key (product_id:%s) total_quantity query' % id)
                continue
            report = self.reports[id]
            report.stock_quantity = stock_quantity or 0
            report.vacant_quantity = vacant_quantity or 0

    def get_order_data(self, all_period=True):
        # 購入件数クエリ
        query = OrderedProduct.query\
            .join(Order).filter(Order.canceled_at==None)\
            .join(Product).filter(Product.id==OrderedProduct.product_id)
        query = self.add_sales_segment_filter(query)
        if self.form.performance_id.data:
            query = query.filter(Order.performance_id==self.form.performance_id.data)
        elif self.form.event_id.data:
            query = query.join(StockType).filter(StockType.event_id==self.form.event_id.data)

        if not all_period:
            if self.form.limited_from.data:
                query = query.filter(Order.created_at >= self.form.limited_from.data)
            if self.form.limited_to.data:
                query = query.filter(Order.created_at < self.form.limited_to.data)

        # 入金済み
        paid_query = query.filter(Order.paid_at!=None)
        paid_query = paid_query.with_entities(
            func.ifnull(Product.base_product_id, Product.id),
            func.sum(OrderedProduct.quantity)
        ).group_by(func.ifnull(Product.base_product_id, Product.id))

        for id, paid_quantity in paid_query.all():
            if id not in self.reports:
                logger.warn('invalid key (product_id:%s) paid_quantity query' % id)
                continue
            record = self.reports[id]
            if all_period:
                record.total_paid_quantity += paid_quantity
            else:
                record.paid_quantity += paid_quantity

        # 未入金
        unpaid_query = query.filter(Order.paid_at==None)
        unpaid_query = unpaid_query.with_entities(
            func.ifnull(Product.base_product_id, Product.id),
            func.sum(OrderedProduct.quantity)
        ).group_by(func.ifnull(Product.base_product_id, Product.id))

        for id, unpaid_quantity in unpaid_query.all():
            if id not in self.reports:
                logger.warn('invalid key (product_id:%s) unpaid_quantity query' % id)
                continue
            record = self.reports[id]
            if all_period:
                record.total_unpaid_quantity += unpaid_quantity
            else:
                record.unpaid_quantity += unpaid_quantity

    def sort_data(self):
        return sorted(self.reports.values(), key=lambda x:(x.stock_type_id, x.stock_id, x.product_name, x.product_price))

    def sort_and_merge_data(self):
        merged_records = {}
        merged_record = None
        pre_merge_key = None
        for record in self.sort_data():
            merge_key = (record.stock_type_id, record.stock_id, record.product_name, record.product_price)
            if merged_record:
                if pre_merge_key == merge_key:
                    merged_record.unpaid_quantity += record.unpaid_quantity
                    merged_record.paid_quantity += record.paid_quantity
                    merged_record.total_unpaid_quantity += record.total_unpaid_quantity
                    merged_record.total_paid_quantity += record.total_paid_quantity
                    continue
                merged_records[merged_record.product_id] = merged_record
            merged_record = record
            pre_merge_key = merge_key
        else:
            merged_records[merged_record.product_id] = merged_record
        self.reports = merged_records
        self.create_group_key_to_reports()
        return self.sort_data()

    def group_key_to_reports(self, key):
        return sorted(self._group_key_to_reports[key], key=lambda x:(x.stock_type_id, x.stock_id, x.product_name, x.product_price))

    def create_group_key_to_reports(self):
        self._group_key_to_reports = {}
        for report in self.reports.values():
            if report.group_key() not in self._group_key_to_reports:
                self._group_key_to_reports[report.group_key()] = []
            self._group_key_to_reports[report.group_key()].append(report)

    def calculate_total(self):
        total = SalesDetailReportRecord()
        for key in self._group_key_to_reports.keys():
            for i, report in enumerate(self.group_key_to_reports(key)):
                if i == 0:
                    total.stock_quantity += report.stock_quantity
                    total.vacant_quantity += report.vacant_quantity
                total.unpaid_quantity += report.unpaid_quantity
                total.paid_quantity += report.paid_quantity
                total.sum_amount += (report.paid_quantity + report.unpaid_quantity) * report.product_price
                total.total_unpaid_quantity += report.total_unpaid_quantity
                total.total_paid_quantity += report.total_paid_quantity
                total.total_sum_amount += (report.total_paid_quantity + report.total_unpaid_quantity) * report.product_price
        self.total = total


class PerformanceReporter(object):

    def __init__(self, form, performance):
        self.form = form
        self.performance = performance
        self.reporters = {}

        # 公演合計のレポート
        self.form.sales_segment_group_id.data = None
        self.total = SalesDetailReporter(self.form)

        # 販売区分別のレポート
        for sales_segment in performance.sales_segments:
            if not sales_segment.public:
                continue
            if (form.limited_from.data and sales_segment.end_at < todatetime(form.limited_from.data)) or\
               (form.limited_to.data and todatetime(form.limited_to.data) < sales_segment.start_at):
                continue
            self.form.sales_segment_group_id.data = sales_segment.sales_segment_group_id
            self.reporters[sales_segment] = SalesDetailReporter(form)

    def sort_index(self):
        return sorted(self.reporters.keys(), key=lambda x:(x.order, x.name))

    def get_reporter(self, sales_segment):
        return self.reporters[sales_segment]


class EventReporter(object):

    def __init__(self, form, event):
        self.form = form
        self.event = event
        self.reporters = {}

        # 公演別のレポート
        for performance in event.performances:
            if not performance.public:
                continue
            end_on = performance.end_on or performance.start_on
            if form.limited_from.data and end_on < todatetime(form.limited_from.data):
                continue
            self.form.performance_id.data = performance.id
            self.reporters[performance] = PerformanceReporter(form, performance)

    def sort_index(self):
        return sorted(self.reporters.keys(), key=lambda x:(x.start_on, x.name))

    def get_reporter(self, performance):
        return self.reporters[performance]


def sendmail(settings, recipient, subject, html):
    sender = settings['mail.message.sender']
    mailer = Mailer(settings)
    mailer.create_message(
        sender = sender,
        recipient = recipient,
        subject = subject,
        body = '',
        html = html.text
    ) 
    try:
        mailer.send(sender, recipient.split(','))
        return True
    except Exception, e:
        logging.error(u'メール送信失敗 %s' % e.message)
        return False
