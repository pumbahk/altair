# -*- coding: utf-8 -*-

from datetime import datetime, date

from pyramid.path import AssetResolver
from sqlalchemy.sql import func, and_

from altair.app.ticketing.core.models import Stock, StockType, Seat, Site, Performance, Venue, SalesSegment, SalesSegmentGroup
from altair.app.ticketing.formatter import Japanese_Japan_Formatter

from . import xls_export
from . import sheet as report_sheet
from .util import DateTimeFormatter

def get_report_kind(report_type):
    # 追券か返券かを明細タイプから判別して返す
    if report_type in ('return', 'final_return'):
        return 'returns'
    return 'stocks'

def get_report_title(report_type):
    report_types = {
        'stock':u'仕入明細',
        'unsold':u'残席明細',
        'sold':u'販売済座席明細',
        'assign':u'配券明細',
        'add':u'追券明細',
        'return':u'返券明細',
        'final_return':u'最終返券明細'
    }
    return report_types[report_type] if report_type in report_types else ''

class DoesNotExistReportType(Exception):
    pass

def exporter_factory(event, stock_holder=None, report_type=None, *args, **kwds):
    """適切なExporterを生成して返す
    """
    if report_type is None:
        return export_for_sales(event)
    elif report_type in ('stock', 'unsold'):
        return export_for_stock_holder(event, stock_holder, report_type, *args, **kwds)
    elif report_type == 'sold':
        return export_for_sold_seats(event, stock_holder, report_type, *args, **kwds)
    else:
        raise DoesNotExistReportType('This report type does not exist: {0}'.format(repr(report_type)))



def export_for_sold_seats(event, stock_holder, report_type, performanceids=None):
    """指定したEvent,StockHolderの販売済座席のレポートをExporterで返す
    """
    if performanceids is None: # default is all pattern
        performanceids = [perf.id for perf in event.sorted_performances()]

    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "altair.app.ticketing:/templates/reports/sold_seats_report_template.xls").abspath()
    exporter = xls_export.SoldSeatsExporter(template=template_path)
    formatter = DateTimeFormatter()

    report_title = get_report_title(report_type)
    today = date.today()

    is_target = lambda perf: perf.id in performanceids
    for i, performance in enumerate(filter(is_target, event.sorted_performances())):
        sheet_num = i + 1
        dt = formatter.format_datetime_for_sheet_name(performance.start_on)
        sheet_name = u"%s_%d" % (dt, sheet_num)
        # 一つ目のシートは追加せずに取得
        if i == 0:
            sheet = exporter.workbook.get_sheet(0)
            sheet.set_name(sheet_name)
        else:
            sheet = exporter.add_sheet(sheet_name)
        table_creator = report_sheet.SoldTableCreator(performance, stock_holder, today)
        tables = table_creator.generate_table()

        report_sheet.process_sheet(exporter, formatter, sheet, report_title, event, performance, stock_holder, tables)
    return exporter

def export_for_stock_holder(event, stock_holder, report_type, performanceids=None):
    """指定したEvent,StockHolderの仕入明細/残席明細レポートをExporterで返す
    """

    if performanceids is None: # default is all pattern
        performanceids = [perf.id for perf in event.sorted_performances()]

    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "altair.app.ticketing:/templates/reports/assign_template.xls").abspath()
    exporter = xls_export.SeatAssignExporter(template=template_path)
    formatter = DateTimeFormatter()

    kind = get_report_kind(report_type)
    report_title = get_report_title(report_type)
    today = date.today()

    is_target = lambda perf: perf.id in performanceids
    for i, performance in enumerate(filter(is_target, event.sorted_performances())):
        sheet_num = i + 1
        dt = formatter.format_datetime_for_sheet_name(performance.start_on)
        sheet_name = u"%s_%d" % (dt, sheet_num)
        # 一つ目のシートは追加せずに取得
        if i == 0:
            sheet = exporter.workbook.get_sheet(0)
            sheet.set_name(sheet_name)
        else:
            sheet = exporter.add_sheet(sheet_name)

        # PerformanceごとのStockを取得
        stock_records = []
        stocks = Stock.query \
                      .join(StockType, StockType.id == Stock.stock_type_id)\
                      .filter(Stock.performance_id == performance.id)\
                      .filter(Stock.stock_holder_id == stock_holder.id)\
                      .order_by(StockType.display_order).all()

        # 席種ごとのオブジェクトを作成
        for stock in stocks:
            stock_type = stock.stock_type
            if not stock_type.disp_reports:
                continue

            # Stock
            params = dict(seat_type=stock_type.name)
            if report_type == 'unsold':
                params.update(stocks_label=u'残席数')
            stock_record = report_sheet.StockRecord(**params)
            # 数受けの場合
            if stock_type.quantity_only:
                seat_record = report_sheet.SeatRecord(
                    block=stock_type.name,
                    quantity=stock.stock_status.quantity if report_type == 'unsold' else stock.quantity,
                    kind=kind,
                    date=today
                )
                stock_record.records.append(seat_record)
            else:
                # Seat
                seats = Seat.filter(Seat.stock_id==stock.id).order_by(Seat.name).all()
                seat_sources = map(report_sheet.seat_source_from_seat, seats)
                seat_records = report_sheet.seat_records_from_seat_sources(seat_sources, report_type, kind=kind, date=today)
                for seat_record in seat_records:
                    stock_record.records.append(seat_record)
            stock_records.append(stock_record)
        report_sheet.process_sheet(exporter, formatter, sheet, report_title, event, performance, stock_holder, stock_records)
    return exporter

def export_for_sales(event):
    """販売日程管理表をExporterで返す
    """
    assetresolver = AssetResolver()
    template_path = assetresolver.resolve("altair.app.ticketing:/templates/reports/sales_schedule_report_template.xls").abspath()
    formatter = DateTimeFormatter()
    exporter = xls_export.SalesScheduleReportExporter(template=template_path, organization_name=event.organization.name)

    # 会場ごとにシートを生成
    site_query = Site.query.join(Venue).filter(Venue.deleted_at==None)
    site_query = site_query.join(Performance).filter(Performance.event_id==event.id).distinct()
    for site in site_query:
        sheet = exporter.add_sheet(site.name)
        price_tables = dict()

        # Event
        data = report_sheet.SalesScheduleRecord(
            event_title=event.title,
            output_datetime=formatter.format_date(datetime.now()),
            venue_name=site.name
        )

        # SalesSegment
        query = SalesSegmentGroup.query.filter(and_(SalesSegmentGroup.event_id==event.id, SalesSegmentGroup.public==True))
        query = query.join(SalesSegment).filter(SalesSegment.deleted_at==None)
        query = query.join(Performance).filter(Performance.deleted_at==None)
        query = query.join(Venue).filter(Venue.deleted_at==None)
        query = query.join(Site).filter(Site.id==site.id).distinct()
        for ssg in query:
            record = report_sheet.SalesScheduleSalesRecord(
                sales_seg=ssg.name,
                sales_start=(ssg.start_at and formatter.format_datetime(ssg.start_at)),
                sales_end=(ssg.end_at and formatter.format_datetime(ssg.end_at)),
                margin_ratio=unicode(ssg.margin_ratio),
                refund_ratio=unicode(ssg.refund_ratio),
                printing_fee=u'{0:,g}'.format(ssg.printing_fee),
                registration_fee=u'{0:,g}'.format(ssg.registration_fee)
            )
            data.sales.append(record)

        # Performance
        query = Performance.query.filter(Performance.event_id==event.id)
        query = query.join(Venue).filter(Venue.deleted_at==None)
        query = query.join(Site).filter(Site.id==site.id)
        for p in query:
            # Price
            sales_segments = SalesSegment.query.filter(and_(SalesSegment.performance_id==p.id, SalesSegment.public==True)).all()
            price_records = dict()  # (Product.display_order, StockType.name, TicketBundle.name, Product.price) = [SalesSegmentGroup.name,]
            for sales_segment in sales_segments:
                for product in sales_segment.products:

                    if not product.seat_stock_type.disp_reports:
                        continue

                    ticket_type = None
                    if product.items and product.items[0].ticket_bundle:
                        ticket_type = product.items[0].ticket_bundle.name
                    key = (product.display_order, product.seat_stock_type.name, ticket_type, int(product.price))
                    if key not in price_records:
                        price_records[key] = []
                    price_records[key].append(sales_segment.sales_segment_group.name)

            price_table = report_sheet.SalesSchedulePriceRecord()
            for key, value in sorted(price_records.items(), key=lambda x:(x[1], x[0])):
                record = report_sheet.SalesSchedulePriceRecordRecord(
                    sales_segment=value,
                    seat_type=key[1],
                    ticket_type=key[2],
                    price=Japanese_Japan_Formatter().format_currency(key[3])
                )
                price_table.records.append(record)

            label = None
            for k, v in price_tables.items():
                if v.get_record() == price_table.get_record():
                    label = k
                    break
            if label is None:
                label = u'%s%s' % (u'価格表', len(price_tables) + 1)
                price_tables[label] = price_table

            end_at = SalesSegment.query.filter(and_(SalesSegment.performance_id==p.id, SalesSegment.public==True))\
                                       .with_entities(func.max(SalesSegment.end_at)).scalar()
            record = report_sheet.SalesSchedulePerformanceRecord(
                datetime_=(p.start_on and formatter.format_date(p.start_on)),
                open_=(p.open_on and formatter.format_time(p.open_on)),
                start=(p.start_on and formatter.format_time(p.start_on)),
                price_name=label,
                sales_end=(end_at and formatter.format_date(end_at)),
                submit_order=None,
                submit_pay=None,
                pay_datetime=None
            )
            data.performances.append(record)

        # Price
        for label in sorted(price_tables.keys()):
            price_table = price_tables[label]
            price_table.name = label
            data.prices.append(price_table)

        exporter.write_data(sheet, data.get_record())

    exporter.remove_templates()
    return exporter
