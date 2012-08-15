# -*- coding: utf-8 -*-

from pyramid.path import AssetResolver

from ticketing.core.models import Event, Performance, StockHolder, StockType, Stock
from ticketing.core.models import SeatAttribute, Seat
from ticketing.helpers.base import jdatetime

from . import xls_export
from . import sheet as report_sheet


def export_for_stock_holder(event, stock_holder):
    """指定したEvent,StockHolderのレポートをExporterで返す
    """
    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "ticketing:/templates/reports/assign_template.xls").abspath()
    exporter = xls_export.SeatAssignExporter(template=template_path)
    # Performance
    query = Performance.filter(Performance.event_id==event.id)
    query = query.order_by(Performance.id)
    performances = list(query)
    for i, performance in enumerate(performances):
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
        stock_query = Stock \
            .filter(Stock.performance_id==performance.id) \
            .filter(Stock.stock_holder_id==stock_holder.id) \
            .order_by(Stock.stock_type_id)
        stocks = list(stock_query)
        # 席種ごとのオブジェクトを作成
        for stock in stocks:
            stock_type = StockType.get(stock.stock_type_id)
            # Stock
            stock_record = report_sheet.StockRecord(seat_type=stock_type.name)
            # 数受けの場合
            if stock_type.quantity_only:
                seat_record = report_sheet.SeatRecord(
                    block=stock_type.name,
                    quantity=stock.quantity)
                stock_record.records.append(seat_record)
            else:
                # Seat
                query = Seat.filter(Seat.stock_id==stock.id)
                seats = query.order_by(Seat.name)
                seat_sources = map(report_sheet.seat_source_from_seat, seats)
                seat_records = report_sheet.seat_records_from_seat_sources(seat_sources)
                for seat_record in seat_records:
                    stock_record.records.append(seat_record)
            stock_records.append(stock_record)
        report_sheet.process_sheet(exporter, sheet, event, performance, stock_holder, stock_records)
    return exporter


def export_for_stock_holder_unsold(event, stock_holder):
    """指定したEvent,StockHolderの残席明細をExporterで返す
    """
    assetresolver = AssetResolver()
    template_path = assetresolver.resolve(
        "ticketing:/templates/reports/assign_template.xls").abspath()
    exporter = xls_export.SeatAssignExporter(template=template_path)
    # Performance
    query = Performance.filter(Performance.event_id==event.id)
    query = query.order_by(Performance.id)
    performances = list(query)
    for i, performance in enumerate(performances):
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
        stock_query = Stock \
            .filter(Stock.performance_id==performance.id) \
            .filter(Stock.stock_holder_id==stock_holder.id) \
            .order_by(Stock.stock_type_id)
        stocks = list(stock_query)
        # 席種ごとのオブジェクトを作成
        for stock in stocks:
            stock_type = StockType.get(stock.stock_type_id)
            # Stock
            stock_record = report_sheet.StockRecord(
                seat_type=stock_type.name,
                stocks_label=u"残席数",
            )
            # 数受けの場合
            if stock_type.quantity_only:
                seat_record = report_sheet.SeatRecord(
                    block=stock_type.name,
                    quantity=stock.quantity)
                stock_record.records.append(seat_record)
            else:
                # Seat
                query = Seat.filter(Seat.stock_id==stock.id)
                seats = query.order_by(Seat.name)
                seat_sources = map(report_sheet.seat_source_from_seat, seats)
                seat_records = report_sheet.seat_records_from_seat_sources_unsold(seat_sources)
                for seat_record in seat_records:
                    stock_record.records.append(seat_record)
            stock_records.append(stock_record)
        report_sheet.process_sheet(exporter, sheet, event, performance, stock_holder, stock_records)
    return exporter
