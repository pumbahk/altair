# -*- coding: utf-8 -*-

import logging
import xlwt
import xlrd
from xlutils.copy import copy
from time import strftime

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from pyramid.response import Response

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, StockHolder, Performance
from altair.app.ticketing.events.reports import reporting
from altair.app.ticketing.events.reports.forms import ReportStockForm, ReportByStockHolderForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class Reports(BaseView):

    @view_config(route_name='reports.index', renderer='altair.app.ticketing:templates/events/report.html')
    def download_index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)
        return {
            'form_stock':ReportStockForm(),
            'form_stock_holder':ReportByStockHolderForm(event_id=event_id),
            'event':event,
            'performances': event.performances,,
        }

    @view_config(route_name='reports.sales', request_method='POST')
    def download_sales(self):
        """販売日程管理表ダウンロード
        """
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        # CSVファイル生成
        exporter = reporting.export_for_sales(event)

        # 出力ファイル名
        filename = "sales_report_%(code)s_%(datetime)s.xls" % dict(
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)

    @view_config(route_name='reports.stocks', request_method='POST', renderer='altair.app.ticketing:templates/events/report.html')
    def download_stocks(self):
        """仕入明細ダウンロード
        """
        # Event
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        # StockHolder
        stock_holders = StockHolder.get_own_stock_holders(event=event)
        if stock_holders is None:
            raise HTTPNotFound("StockHolder is not found event_id=%s" % event_id)

        f = ReportStockForm(self.request.params, event_id=event_id)
        if not f.validate():
            return {
                'form_stock':f,
                'form_stock_holder':ReportByStockHolderForm(event_id=event_id),
                'event':event,
                'performances': event.performances,
            }

        # CSVファイル生成
        performanceids = self.request.POST.getall('performance_id')
        exporter = reporting.export_for_stock_holder(event, stock_holders[0], f.report_type.data, performanceids=performanceids)

        # 出力ファイル名
        filename = "%(report_type)s_%(code)s_%(datetime)s.xls" % dict(
            report_type=f.report_type.data,
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)

    @view_config(route_name='reports.stocks_by_stockholder', request_method='POST', renderer='altair.app.ticketing:templates/events/report.html')
    def download_stocks_by_stockholder(self):
        """配券明細ダウンロード
        """
        # Event
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        
        # StockHolder
        stock_holder_id = int(self.request.params.get('stock_holder_id', 0))
        stock_holder = StockHolder.get(stock_holder_id)
        if stock_holder is None:
            raise HTTPNotFound("StockHolder is not found id=%s" % stock_holder_id)

        f = ReportByStockHolderForm(self.request.params, event_id=event_id)
        if not f.validate():
            return {
                'form_stock':ReportStockForm(),
                'form_stock_holder':f,
                'event':event,
                'performances': event.performances,
            }

        # CSVファイル生成
        performanceids = self.request.POST.getall('performance_id')
        exporter = reporting.export_for_stock_holder(event, stock_holder, f.report_type.data, performanceids=performanceids)
        
        # 出力ファイル名
        filename = "%(report_type)s_%(code)s_%(datetime)s.xls" % dict(
            report_type=f.report_type.data,
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)
