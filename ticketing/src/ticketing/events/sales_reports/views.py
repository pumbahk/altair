# -*- coding: utf-8 -*-

import logging

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func

from ticketing.models import merge_session_with_post
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, Organization, ReportSetting, Mailer
from ticketing.core.models import StockType, StockHolder, StockStatus, Stock, Performance, Product, ProductItem, SalesSegment
from ticketing.core.models import Order, OrderedProduct, OrderedProductItem
from ticketing.events.forms import EventForm
from ticketing.events.performances.forms import PerformanceForm
from ticketing.events.sales_reports.forms import SalesReportForm, SalesReportMailForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReports(BaseView):

    def _get_sales_summary(self, form, group='Event'):
        reports = {}

        # 自社分のみが対象
        stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=self.context.organization.user_id)]

        # 配席数、在庫数
        query = Event.query.filter(Event.organization_id==self.context.user.organization_id)\
            .outerjoin(Performance).filter(Performance.deleted_at==None)\
            .outerjoin(Stock).filter(Stock.deleted_at==None, Stock.stock_holder_id.in_(stock_holder_ids))\
            .outerjoin(StockStatus).filter(StockStatus.deleted_at==None)
        if form.performance_id.data:
            query = query.filter(Performance.id==form.performance_id.data)
        if form.event_id.data:
            query = query.filter(Event.id==form.event_id.data)

        if group == 'Performance':
            query = query.group_by(Performance.id)\
                .with_entities(
                    Performance.id,
                    Performance.name,
                    Performance.start_on,
                    func.sum(Stock.quantity),
                    func.sum(StockStatus.quantity)
                )
        else:
            query = query.group_by(Event.id)\
                .with_entities(
                    Event.id,
                    Event.title,
                    Event.id, # dummy
                    func.sum(Stock.quantity),
                    func.sum(StockStatus.quantity)
                )

        for id, title, start_on, total_quantity, vacant_quantity in query.all():
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
            )

        '''
        # 売上合計、手数料合計
        query = Event.query.filter(Event.organization_id==self.context.user.organization_id)\
            .outerjoin(Performance).filter(Performance.deleted_at==None)\
            .outerjoin(Order).filter(Order.canceled_at==None, Order.deleted_at==None)
        if form.limited_from.data:
            query = query.filter(Order.created_at > form.limited_from.data)
        if form.limited_to.data:
            query = query.filter(Order.created_at < form.limited_to.data)
        if form.performance_id.data:
            query = query.filter(Performance.id==form.performance_id.data)
        if form.event_id.data:
            query = query.filter(Event.id==form.event_id.data)

        if group == 'Performance':
            query = query.group_by(Performance.id)\
                .with_entities(
                    Performance.id,
                    func.sum(Order.total_amount).label('total_amount'),
                    func.sum(Order.system_fee + Order.transaction_fee + Order.delivery_fee).label('fee_amount')
                )
        else:
            query = query.group_by(Event.id)\
                .with_entities(
                    Event.id,
                    func.sum(Order.total_amount).label('total_amount'),
                    func.sum(Order.system_fee + Order.transaction_fee + Order.delivery_fee).label('fee_amount')
                )

        for id, total_amount, fee_amount in query.all():
            reports[id].update(dict(total_amount=total_amount or 0, fee_amount=fee_amount or 0))
        '''

        # 販売金額、販売枚数
        query = Event.query.filter(Event.organization_id==self.context.user.organization_id)\
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
            query = query.group_by(Performance.id)\
                .with_entities(
                    Performance.id,
                    func.sum(OrderedProduct.price * OrderedProduct.quantity).label('price_amount'),
                    func.sum(OrderedProduct.quantity).label('product_quantity')
                )
        else:
            query = query.group_by(Event.id)\
                .with_entities(
                    Event.id,
                    func.sum(OrderedProduct.price * OrderedProduct.quantity).label('price_amount'),
                    func.sum(OrderedProduct.quantity).label('product_quantity')
                )

        for id, price_amount, product_quantity in query.all():
            reports[id].update(dict(price_amount=price_amount or 0, product_quantity=product_quantity or 0))

        return reports.values()

    def _get_performance_sales_summary(self, form):
        performance_reports = {}

        # 自社分のみが対象
        stock_holder_ids = [sh.id for sh in StockHolder.get_own_stock_holders(user_id=self.context.organization.user_id)]

        # 商品ごとの情報、配席数、在庫数
        query = StockType.query.filter(StockType.id==Stock.stock_type_id)\
            .join(Product).filter(Product.seat_stock_type_id==StockType.id)\
            .outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)\
            .outerjoin(ProductItem).filter(ProductItem.product_id==Product.id, ProductItem.performance_id==form.performance_id.data)\
            .outerjoin(Stock).filter(Stock.id==ProductItem.stock_id, Stock.stock_holder_id.in_(stock_holder_ids))\
            .outerjoin(StockHolder).filter(StockHolder.id==Stock.stock_holder_id)\
            .outerjoin(StockStatus).filter(StockStatus.stock_id==Stock.id)\
            .with_entities(
                StockType.id.label('stock_type_id'),
                StockType.name.label('stock_type_name'),
                Product.id.label('product_id'),
                Product.name.label('product_name'),
                Product.price.label('product_price'),
                func.sum(Stock.quantity).label('total_quantity'),
                func.sum(StockStatus.quantity).label('vacant_quantity'),
                StockHolder.id.label('stock_holder_id'),
                StockHolder.name.label('stock_holder_name'),
                SalesSegment.name.label('sales_segment_name'),
            )
        for row in query.group_by(Product.id).all():
            performance_reports[row[2]] = dict(
                stock_type_id=row[0],
                stock_type_name=row[1],
                product_id=row[2],
                product_name=row[3],
                product_price=row[4],
                total_quantity=row[5],
                vacant_quantity=row[6],
                stock_holder_id=row[7],
                stock_holder_name=row[8],
                sales_segment_name=row[9],
                order_quantity=0,
                paid_quantity=0,
                unpaid_quantity=0,
            )

        # 入金済み
        query = OrderedProduct.query.join(Order).filter(Order.performance_id==form.performance_id.data)\
            .filter(Order.canceled_at==None, Order.paid_at!=None)\
            .join(Product).filter(Product.id==OrderedProduct.product_id)\
            .outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)\
            .with_entities(OrderedProduct.product_id, func.sum(OrderedProduct.quantity))
        if form.limited_from.data:
            query = query.filter(Order.created_at > form.limited_from.data)
        if form.limited_to.data:
            query = query.filter(Order.created_at < form.limited_to.data)

        for id, paid_quantity in query.group_by(OrderedProduct.product_id).all():
            performance_reports[id].update(dict(paid_quantity=paid_quantity or 0))

        # 未入金
        query = OrderedProduct.query.join(Order).filter(Order.performance_id==form.performance_id.data)\
            .filter(Order.canceled_at==None, Order.paid_at==None)\
            .join(Product).filter(Product.id==OrderedProduct.product_id)\
            .outerjoin(SalesSegment).filter(SalesSegment.id==Product.sales_segment_id, SalesSegment.id==form.sales_segment_id.data)\
            .with_entities(OrderedProduct.product_id, func.sum(OrderedProduct.quantity))
        if form.limited_from.data:
            query = query.filter(Order.created_at > form.limited_from.data)
        if form.limited_to.data:
            query = query.filter(Order.created_at < form.limited_to.data)

        for id, unpaid_quantity in query.group_by(OrderedProduct.product_id).all():
            performance_reports[id].update(dict(unpaid_quantity=unpaid_quantity or 0))

        return performance_reports.values()

    @view_config(route_name='sales_reports.index', renderer='ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportForm(self.request.params)
        event_reports = self._get_sales_summary(form)

        form_total = SalesReportForm(self.request.params)
        form_total.limited_from.data = None
        form_total.limited_to.data = None
        event_total_reports = self._get_sales_summary(form_total)

        return {
            'form':form,
            'event_reports':event_reports,
            'event_total_reports':event_total_reports
        }

    @view_config(route_name='sales_reports.event', renderer='ticketing:templates/sales_reports/event.html')
    def event(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        form = SalesReportForm(self.request.params, event_id=event_id)
        event_report = self._get_sales_summary(form)
        performances_reports = self._get_sales_summary(form, group='Performance')

        form_total = SalesReportForm(self.request.params, event_id=event_id)
        form_total.limited_from.data = None
        form_total.limited_to.data = None
        event_total_report = self._get_sales_summary(form_total)
        performances_total_reports = self._get_sales_summary(form_total, group='Performance')

        return {
            'form':form,
            'event':event,
            'event_report':event_report.pop(),
            'event_total_report':event_total_report.pop(),
            'form_event':EventForm(),
            'form_performance':PerformanceForm(),
            'form_report_mail':SalesReportMailForm(organization_id=self.context.user.organization_id, event_id=event_id),
            'report_settings':ReportSetting.filter_by(event_id=event_id).all(),
            'performances_reports':performances_reports,
            'performances_total_reports':performances_total_reports,
        }

    @view_config(route_name='sales_reports.performance', renderer='ticketing:templates/sales_reports/performance.html')
    def performance(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            raise HTTPNotFound('performance id %d is not found' % performance_id)
        report_by_sales_segment = {}
        for sales_segment in performance.event.sales_segments:
            form = SalesReportForm(performance_id=performance_id, sales_segment_id=sales_segment.id)
            report_by_sales_segment[sales_segment.name] = self._get_performance_sales_summary(form)

        return {
            'performance':performance,
            'report_by_sales_segment':report_by_sales_segment,
        }

    @view_config(route_name='sales_reports.preview', renderer='ticketing:templates/sales_reports/preview.html')
    def preview(self):
        form = SalesReportForm(self.request.params)
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        report_settings = ReportSetting.filter_by(event_id=event_id).all()
        if (form.recipient.data is None):
            form.recipient.data = ','.join([rs.operator.email for rs in report_settings])
        if (form.subject.data is None):
            form.subject.data = u'楽天チケット[申込状況(速報)]' + event.title

        return {
            'form':form,
            'event_id':event_id,
        }

    @view_config(route_name='sales_reports.mail_body', renderer='ticketing:templates/sales_reports/mail_body.html')
    def mail_body(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        form = SalesReportForm(self.request.params)
        performances_reports = {}
        for performance in event.performances:
            report_by_sales_segment = {}
            for sales_segment in event.sales_segments:
                form = SalesReportForm(performance_id=performance.id, sales_segment_id=sales_segment.id)
                report_by_sales_segment[sales_segment.name] = self._get_performance_sales_summary(form)

            performances_reports[performance.id] = dict(
                performance=performance,
                report_by_sales_segment=report_by_sales_segment
            )

        return {
            'form':form,
            'performances_reports':performances_reports,
        }

    @view_config(route_name='sales_reports.send_mail', renderer='ticketing:templates/sales_reports/preview.html')
    def send_mail(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        form = SalesReportForm(self.request.params)
        if form.validate():
            performances_reports = {}
            for performance in event.performances:
                report_by_sales_segment = {}
                for sales_segment in event.sales_segments:
                    sales_report_form = SalesReportForm(performance_id=performance.id, sales_segment_id=sales_segment.id)
                    report_by_sales_segment[sales_segment.name] = self._get_performance_sales_summary(sales_report_form)
                performances_reports[performance.id] = dict(
                  performance=performance,
                  report_by_sales_segment=report_by_sales_segment
                )
            render_param = {
                'performances_reports':performances_reports,
            }

            settings = self.request.registry.settings
            sender = settings['mail.message.sender']
            recipient =  form.recipient.data
            subject = form.subject.data
            html = render_to_response('ticketing:templates/sales_reports/mail_body.html', render_param, request=self.request)
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
                self.request.session.flash(u'レポートメールを送信しました')
            except Exception, e:
                logging.error(u'メール送信失敗 %s' % e.message)
                self.request.session.flash(u'メール送信に失敗しました')
            #return HTTPFound(location=route_path('sales_reports.preview', self.request, event_id=event_id))
        else:
            self.request.session.flash(u'入力されていません')

        return {
            'form':form,
            'event_id':event_id,
        }


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReportMails(BaseView):

    @view_config(route_name='sales_reports.mail.new', request_method='POST', renderer='ticketing:templates/sales_reports/_form.html')
    def new_post(self):
        event_id = int(self.request.POST.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        f = SalesReportMailForm(self.request.POST, organization_id=self.context.user.organization_id, event_id=event_id)
        if f.validate():
            report_mail = merge_session_with_post(ReportSetting(), f.data)
            report_mail.save()

            self.request.session.flash(u'新規メール送信先を保存しました')
            return render_to_response('ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
            }

    @view_config(route_name='sales_reports.mail.delete')
    def delete(self):
        report_setting_id = int(self.request.matchdict.get('report_setting_id', 0))
        report_setting = ReportSetting.get(report_setting_id)
        if report_setting is None:
            raise HTTPNotFound('report_setting id %d is not found' % report_setting_id)

        location = route_path('sales_reports.event', self.request, event_id=report_setting.event.id)
        try:
            report_setting.delete()
            self.request.session.flash(u'選択した送信先を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
