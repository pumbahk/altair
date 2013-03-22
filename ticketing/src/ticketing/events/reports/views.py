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

from ticketing.models import record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, StockHolder
from ticketing.events.forms import EventForm
from ticketing.events.reports import reporting
from ticketing.events.reports.forms import ReportStockForm, ReportByStockHolderForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class Reports(BaseView):

    @view_config(route_name='reports.index', renderer='ticketing:templates/events/report.html')
    def download_index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        return {
            'form_stock':ReportStockForm(),
            'form_stock_holder':ReportByStockHolderForm(event_id=event_id),
            'event':event,
        }

    @view_config(route_name='reports.sales', request_method='POST', renderer='ticketing:templates/events/report.html')
    def download_sales(self):
        """販売日程管理表ダウンロード
        """
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        # copy from template.xls
        rb = xlrd.open_workbook('src/ticketing/templates/reports/sales_report_template.xls', formatting_info=True)
        wb = copy(rb)

        # find data as json format

        # add data to xls sheet
        #book = xlwt.Workbook()
        #book.add_sheet("NewSheet_1")
        #book.save('sample.xls')

        sheet = wb.get_sheet(0)

        # Event
        sheet.write(0, 34, u"(現在日時)")
        sheet.write(5, 0, u"(イベント名)")
        sheet.write(11, 0, u"(販売区分名)")
        sheet.write(11, 12, u"(販売開始日時)")
        sheet.write(11, 18, u"(販売終了日時)")
        sheet.write(11, 30, u"(販売手数料)")
        sheet.write(12, 30, u"(払戻手数料)")
        sheet.write(13, 30, u"(印刷代金)")
        sheet.write(14, 30, u"(登録手数料)")
        sheet.write(16, 0, u"(会場名)")

        # Performance

        #

        '''
        sheet_row_1 = sheet.row(1)
        sheet_row_1.write(0, "A2")
        sheet_row_1.write(1, "B2")
        sheet_row_1.write(2, "C2")
        sheet_row_1.write(3, "D2")
        sheet_row_1.write(4, "E2")
        '''

        # download
        wb.save('sales_report_%s_%s.xls' % (event_id, strftime('%Y%m%d%H%M%S')))

        # temporary redirect
        return HTTPFound(location=route_path('events.report', self.request, event_id=event.id))

        #fname = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
        #f = open(fname)
        #headers = [
        #    ('Content-Type', 'application/octet-stream'),
        #    ('Content-Disposition', 'attachment; filename=%s' % os.path.basename(fname))
        #]
        #response = Response(f.read(), headers=headers)
        #f.close()

        #return response

    @view_config(route_name='reports.stocks', request_method='POST', renderer='ticketing:templates/events/report.html')
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
            }

        # CSVファイル生成
        exporter = reporting.export_for_stock_holder(event, stock_holders[0], f.report_type.data)

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

    @view_config(route_name='reports.stocks_by_stockholder', request_method='POST', renderer='ticketing:templates/events/report.html')
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
            }

        # CSVファイル生成
        exporter = reporting.export_for_stock_holder(event, stock_holder, f.report_type.data)

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
