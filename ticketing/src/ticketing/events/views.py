# -*- coding: utf-8 -*-
import os
import isodate
import json
import logging
import urllib2
import contextlib
import xlwt
import xlrd
from xlutils.copy import copy
from datetime import datetime
from time import strftime

import webhelpers.paginate as paginate
from sqlalchemy import or_
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path
from pyramid.response import Response
from pyramid.path import AssetResolver

from ticketing.models import merge_session_with_post, record_to_multidict, DBSession
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, Performance, StockHolder, StockType, Stock
from ticketing.core.models import SeatAttribute, Seat
from ticketing.events.forms import EventForm
from ticketing.events.performances.forms import PerformanceForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.events.stock_types.forms import StockTypeForm
from ticketing.events.stock_holders.forms import StockHolderForm
from ticketing.products.forms import ProductForm
from ticketing.events.reports import xls_export
from ticketing.events.reports import sheet as report_sheet
from ticketing.helpers.base import jdatetime

from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Events(BaseView):

    @view_config(route_name='events.index', renderer='ticketing:templates/events/index.html')
    def index(self):
        sort = self.request.GET.get('sort', 'Event.id')
        direction = self.request.GET.get('direction', 'desc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Event.filter(Event.organization_id==int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        # search condition
        if self.request.method == 'POST':
            condition = self.request.POST.get('event')
            if condition:
                condition = '%' + condition + '%'
                query = query.filter(or_(Event.code.like(condition), Event.title.like(condition)))
            condition = self.request.POST.get('performance')
            if condition:
                condition = '%' + condition + '%'
                query = query.join(Event.performances)\
                            .filter(or_(Performance.code.like(condition), Performance.name.like(condition)))

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=10,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'events':events,
        }

    @view_config(route_name='events.show', renderer='ticketing:templates/events/show.html')
    def show(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        accounts = event.get_accounts()

        return {
            'event':event,
            'accounts':accounts,
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'form_stock_type':StockTypeForm(event_id=event_id),
            'form_stock_holder':StockHolderForm(organization_id=self.context.user.organization_id, event_id=event_id),
            'form_sales_segment':SalesSegmentForm(event_id=event_id),
            'form_product':ProductForm(event_id=event.id),
        }

    @view_config(route_name='events.new', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def new_get(self):
        f = EventForm(organization_id=self.context.user.organization.id)
        event = Event(organization_id=self.context.user.organization_id)

        event_id = int(self.request.matchdict.get('event_id', 0))
        if event_id:
            event = Event.get(event_id)
            if event is None:
                return HTTPNotFound('event id %d is not found' % event_id)

        event = record_to_multidict(event)
        if 'id' in event: event.pop('id')
        f.process(event)

        return {
            'form':f,
        }

    @view_config(route_name='events.new', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def new_post(self):
        f = EventForm(self.request.POST, organization_id=self.context.user.organization.id)

        if f.validate():
            event = merge_session_with_post(Event(organization_id=self.context.user.organization_id), f.data)
            event.save()

            self.request.session.flash(u'イベントを登録しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
            }

    @view_config(route_name='events.edit', request_method='GET', renderer='ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def edit_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(organization_id=self.context.user.organization.id)
        f.process(record_to_multidict(event))

        if self.request.matched_route.name == 'events.copy':
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='events.edit', request_method='POST', renderer='ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def edit_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            if self.request.matched_route.name == 'events.copy':
                event = merge_session_with_post(Event(organization_id=self.context.user.organization_id), f.data)
            else:
                event = merge_session_with_post(event, f.data)
            event.save()

            self.request.session.flash(u'イベントを保存しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
                'event':event,
            }

    @view_config(route_name='events.delete')
    def delete(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        event.delete()

        self.request.session.flash(u'イベントを削除しました')
        return HTTPFound(location=route_path('events.index', self.request))

    @view_config(route_name='events.send')
    def send(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.query.filter(Event.id==event_id).first()
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        try:
            data = {
                'events':[event.get_cms_data()],
                'created_at':isodate.datetime_isoformat(datetime.now()),
                'updated_at':isodate.datetime_isoformat(datetime.now()),
            }
        except Exception, e:
            logging.info("cms build data error: %s (event_id=%s)" % (e.message, event_id))
            self.request.session.flash(e.message)
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))

        communication_api = get_communication_api(self.request, CMSCommunicationApi)
        req = communication_api.create_connection('api/event/register', json.dumps(data))

        try:
            with contextlib.closing(urllib2.urlopen(req)) as res:
                if res.getcode() == HTTPCreated.code:
                    self.request.session.flash(u'イベントをCMSへ送信しました')
                else:
                    raise urllib2.HTTPError(code=res.getcode())
        except urllib2.HTTPError, e:
            logging.warn("cms sync http error: response status url=(%s) %s" % (e.code, e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.code)
        except urllib2.URLError, e:
            logging.warn("cms sync http error: response status url=(%s) %s" % (e.reason, e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.reason)
        except Exception, e:
            logging.error("cms sync error: %s, %s" % (e.reason, e.message))
            self.request.session.flash(u'イベント送信に失敗しました')

        return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))

    @view_config(route_name='events.report', renderer='ticketing:templates/events/report.html')
    def report(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        # StockHolder
        stock_holders = list(StockHolder \
            .filter(StockHolder.event_id==event_id) \
            .order_by(StockHolder.id))

        f = EventForm(user_id=self.context.user.id)
        f.process(record_to_multidict(event))
        return {
            'form':f,
            'event':event,
            'stock_holders': stock_holders,
        }

    @view_config(route_name='events.report.sales')
    def download_sales_report(self):
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

    @view_config(route_name='events.report.seat_all')
    def download_seat_all(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        assetresolver = AssetResolver()
        template_path = assetresolver.resolve(
            "ticketing:/templates/reports/assign_template.xls").abspath()
        exporter = xls_export.SeatAssignExporter(template=template_path)
        # TODO:Event
        sheet_0 = exporter.workbook.get_sheet(0)
        exporter.set_event_name(sheet_0, event.title)
        # TODO:Performance

        # 出力ファイル名
        filename = "assign_%(code)s_%(datetime)s" % dict(
            code=event.code,  # イベントコード
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % filename)
        ]
        response = Response(exporter.as_string(), headerlist=headers)
        return response

    @view_config(route_name='events.report.seat_stocks')
    def download_seat_stocks(self):
        """仕入明細ダウンロード
        """
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        assetresolver = AssetResolver()
        template_path = assetresolver.resolve(
            "ticketing:/templates/reports/assign_template.xls").abspath()
        exporter = xls_export.SeatAssignExporter(template=template_path)
        # 現在日時
        timestamp = strftime('%Y%m%d%H%M%S')
        # Performance
        query = Performance.filter(Performance.event_id==event_id)
        query = query.order_by(Performance.id)
        performances = list(query)
        # StockHolder
        stock_holder = StockHolder \
            .filter(StockHolder.event_id==event_id) \
            .filter(StockHolder.account_id==self.context.user.id).first()
        if stock_holder is None:
            raise Exception("StockHolder is not found event_id=%s, account_id=%s" % (event_id, self.user.id))

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
                    seats = Seat.filter(Seat.stock_id==stock.id).order_by(Seat.name)
                    seat_sources = map(report_sheet.seat_source_from_seat, seats)
                    seat_records = report_sheet.seat_records_from_seat_sources(seat_sources)
                    for seat_record in seat_records:
                        stock_record.records.append(seat_record)
                stock_records.append(stock_record)
            report_sheet.process_sheet(exporter, sheet, event, performance, stock_records)
        # 出力ファイル名
        filename = "assign_%(code)s_%(datetime)s" % dict(
            code=event.code,  # イベントコード
            datetime=timestamp
        )

        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % filename)
        ]
        response = Response(exporter.as_string(), headerlist=headers)
        return response

    @view_config(route_name='events.report.seat_returns')
    def download_seat_returns(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        assetresolver = AssetResolver()
        template_path = assetresolver.resolve(
            "ticketing:/templates/reports/assign_template.xls").abspath()
        exporter = xls_export.SeatAssignExporter(template=template_path)
        # TODO:Event
        sheet_0 = exporter.workbook.get_sheet(0)
        exporter.set_event_name(sheet_0, event.title)
        # TODO:Performance

        # 出力ファイル名
        filename = "assign_%(code)s_%(datetime)s" % dict(
            code=event.code,  # イベントコード
            datetime=strftime('%Y%m%d%H%M%S')
        )

        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % filename)
        ]
        response = Response(exporter.as_string(), headerlist=headers)
        return response
