# -*- coding: utf-8 -*-

from datetime import date

from pyramid.path import AssetResolver

from ticketing.core.models import Stock
from ticketing.core.models import Seat
from ticketing.helpers.base import jdatetime

from . import xls_export
from . import sheet as report_sheet

def get_kind(report_type):
    # 追券か返券かを明細タイプから判別して返す
    if report_type in ('return', 'final_return'):
        return 'returns'
    return 'stocks'

def get_report_title(report_type):
    report_types = {
        'stock':u'仕入明細',
        'unsold':u'残席明細',
        'assign':u'配券明細',
        'add':u'追券明細',
        'return':u'返券明細',
        'final_return':u'最終返券明細'
    }
    return report_types[report_type] if report_type in report_types else ''

def export_for_stock_holder(event, stock_holder, report_type):
    """指定したEvent,StockHolderのレポートをExporterで返す
    """
    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "ticketing:/templates/reports/assign_template.xls").abspath()
    exporter = xls_export.SeatAssignExporter(template=template_path)
    kind = get_kind(report_type)
    report_title = get_report_title(report_type)
    today = date.today()
    for i, performance in enumerate(event.performances):
        sheet_num = i + 1
        sheet_name = u"%s%d" % (jdatetime(performance.start_on), sheet_num)
        # 一つ目のシートは追加せずに取得
        if i == 0:
            sheet = exporter.workbook.get_sheet(0)
            sheet.set_name(sheet_name)
        else:
            sheet = exporter.add_sheet(sheet_name)
        # PerformanceごとのStockを取得
        stock_records = []
        stocks = Stock.filter_by(performance_id=performance.id)\
                      .filter_by(stock_holder_id=stock_holder.id)\
                      .order_by(Stock.stock_type_id).all()
        # 席種ごとのオブジェクトを作成
        for stock in stocks:
            stock_type = stock.stock_type
            # Stock
            stock_record = report_sheet.StockRecord(seat_type=stock_type.name)
            # 数受けの場合
            if stock_type.quantity_only:
                seat_record = report_sheet.SeatRecord(
                    block=stock_type.name,
                    quantity=stock.quantity,
                    date=today,
                    kind=kind
                )
                stock_record.records.append(seat_record)
            else:
                # Seat
                seats = Seat.filter_by(stock_id=stock.id).order_by(Seat.name).all()
                seat_sources = map(report_sheet.seat_source_from_seat, seats)
                seat_records = report_sheet.seat_records_from_seat_sources(seat_sources, kind=kind)
                for seat_record in seat_records:
                    stock_record.records.append(seat_record)
            stock_records.append(stock_record)
        report_sheet.process_sheet(exporter, sheet, report_title, event, performance, stock_holder, stock_records)
    return exporter

def export_for_stock_holder_unsold(event, stock_holder, report_type):
    """指定したEvent,StockHolderの残席明細をExporterで返す
    """
    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "ticketing:/templates/reports/assign_template.xls").abspath()
    exporter = xls_export.SeatAssignExporter(template=template_path)
    kind = get_kind(report_type)
    report_title = get_report_title(report_type)
    today = date.today()
    # Performance
    for i, performance in enumerate(event.performances):
        sheet_num = i + 1
        sheet_name = u"%s%d" % (jdatetime(performance.start_on), sheet_num)
        # 一つ目のシートは追加せずに取得
        if i == 0:
            sheet = exporter.workbook.get_sheet(0)
            sheet.set_name(sheet_name)
        else:
            sheet = exporter.add_sheet(sheet_name)
        # PerformanceごとのStockを取得
        stock_records = []
        stocks = Stock.filter(Stock.performance_id==performance.id) \
                      .filter(Stock.stock_holder_id==stock_holder.id) \
                      .order_by(Stock.stock_type_id).all()
        # 席種ごとのオブジェクトを作成
        for stock in stocks:
            stock_type = stock.stock_type
            # Stock
            stock_record = report_sheet.StockRecord(
                seat_type=stock_type.name,
                stocks_label=u"残席数",
            )
            # 数受けの場合
            if stock_type.quantity_only:
                seat_record = report_sheet.SeatRecord(
                    block=stock_type.name,
                    quantity=stock.quantity,
                    date=today,
                    kind=kind
                )
                stock_record.records.append(seat_record)
            else:
                # Seat
                seats = Seat.filter(Seat.stock_id==stock.id).order_by(Seat.name).all()
                seat_sources = map(report_sheet.seat_source_from_seat, seats)
                seat_records = report_sheet.seat_records_from_seat_sources(seat_sources, kind=kind, unsold=True)
                for seat_record in seat_records:
                    stock_record.records.append(seat_record)
            stock_records.append(stock_record)
        report_sheet.process_sheet(exporter, sheet, report_title, event, performance, stock_holder, stock_records)
    return exporter
