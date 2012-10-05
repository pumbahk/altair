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

from ticketing.core.models import record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, StockHolder
from ticketing.events.forms import EventForm
from ticketing.events.reports import reporting

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class Reports(BaseView):

    @view_config(route_name='reports.index', renderer='ticketing:templates/events/report.html')
    def report(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(user_id=self.context.user.id)
        f.process(record_to_multidict(event))

        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='reports.sales')
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
        print dir(wb)

        # find data as json format

        # add data to xls sheet
        #book = xlwt.Workbook()
        #book.add_sheet("NewSheet_1")
        #book.save('sample.xls')

        sheet = wb.get_sheet(0)
        print dir(sheet)

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

    @view_config(route_name='reports.seat_stocks')
    def download_seat_stocks(self):
        """仕入明細ダウンロード
        """
        # Event
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        # StockHolder
        stock_holders = StockHolder.get_seller(event)
        if stock_holders is None:
            raise HTTPNotFound("StockHolder is not found event_id=%s" % event_id)

        exporter = reporting.export_for_stock_holder(event, stock_holders[0])

        # 出力ファイル名
        filename = "assign_%(code)s_%(datetime)s.xls" % dict(
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)

    @view_config(route_name='reports.seat_stock_to_stockholder')
    def download_seat_stock_to_stockholder(self):
        """配券明細ダウンロード
        """
        # Event
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        # StockHolder
        stock_holder_id = int(self.request.matchdict.get('stock_holder_id', 0))
        stock_holder = StockHolder.get(stock_holder_id)
        if stock_holder is None:
            raise HTTPNotFound("StockHolder is not found id=%s" % stock_holder_id)

        exporter = reporting.export_for_stock_holder(event, stock_holder)

        # 出力ファイル名
        filename = "assign_%(code)s_%(datetime)s.xls" % dict(
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)

    @view_config(route_name='reports.seat_unsold')
    def download_seat_stock_unsold(self):
        """残席明細ダウンロード
        """
        # Event
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        # StockHolder
        stock_holders = StockHolder.get_seller(event)
        if stock_holders is None:
            raise HTTPNotFound("StockHolder is not found event_id=%s" % event_id)

        exporter = reporting.export_for_stock_holder_unsold(event, stock_holders[0])

        # 出力ファイル名
        filename = "unsold_%(code)s_%(datetime)s.xls" % dict(
            code=event.code,
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', 'attachment; filename=%s' % str(filename))
        ]
        return Response(exporter.as_string(), headers=headers)
