# -*- coding: utf-8 -*-

import logging

import webhelpers.paginate as paginate
import datetime

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
from ticketing.events.sales_reports.forms import SalesReportForm, SalesReportMailForm
from ticketing.events.sales_reports.sendmail import get_sales_summary, get_performance_sales_summary, get_performance_sales_detail

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReports(BaseView):

    @view_config(route_name='sales_reports.index', renderer='ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportForm(self.request.params)
        event_reports = get_sales_summary(form, self.context.organization)

        form_total = SalesReportForm(self.request.params)
        form_total.limited_from.data = None
        form_total.limited_to.data = None
        event_total_reports = get_sales_summary(form_total, self.context.organization)

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
        event_reports = get_sales_summary(form, self.context.organization)
        performances_reports = get_sales_summary(form, self.context.organization, group='Performance')

        form_total = SalesReportForm(self.request.params, event_id=event_id)
        form_total.limited_from.data = None
        form_total.limited_to.data = None
        event_total_reports = get_sales_summary(form_total, self.context.organization)
        performances_total_reports = get_sales_summary(form_total, self.context.organization, group='Performance')

        return {
            'form':form,
            'event_report':event_reports.pop(),
            'event_total_report':event_total_reports.pop(),
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
            form = SalesReportForm(self.request.params, performance_id=performance_id, sales_segment_id=sales_segment.id)
            report_by_sales_segment[sales_segment.name] = get_performance_sales_summary(form, self.context.organization)

        return {
            'form':SalesReportForm(self.request.params, event_id=performance.event_id),
            'performance':performance,
            'report_by_sales_segment':report_by_sales_segment,
        }

    @view_config(route_name='sales_reports.preview', renderer='ticketing:templates/sales_reports/preview.html')
    def preview(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        form = SalesReportForm(self.request.params, event_id=event_id)
        if not form.recipient.data:
            report_settings = ReportSetting.filter_by(event_id=event_id).all()
            form.recipient.data = ','.join([rs.operator.email for rs in report_settings])
        if not form.subject.data:
            form.subject.data = u'[売上レポート] %s' % event.title

        return {
            'form':form,
        }

    @view_config(route_name='sales_reports.mail_body', renderer='ticketing:templates/sales_reports/mail_body.html')
    def mail_body(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        form = SalesReportForm(self.request.params, event_id=event_id)
        event_product = get_performance_sales_summary(form, self.context.organization)
        event_product_total = get_performance_sales_summary(SalesReportForm(event_id=event_id), self.context.organization)
        performances_reports = get_performance_sales_detail(form, event)
     
        return {
            'event_product':event_product,
            'event_product_total':event_product_total,
            'form':form,
            'performances_reports':performances_reports,
        }



    @view_config(route_name='sales_reports.send_mail', renderer='ticketing:templates/sales_reports/preview.html')
    def send_mail(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
     
        form = SalesReportForm(self.request.params, event_id=event_id)
        if form.validate():
            event_product = get_performance_sales_summary(form, self.context.organization)
            event_product_total = get_performance_sales_summary(SalesReportForm(event_id=event_id), self.context.organization)
            performances_reports = get_performance_sales_detail(form, event)

            render_param = {
                'event_product':event_product,
                'event_product_total':event_product_total,
                'form':form,
                'performances_reports':performances_reports
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
        else:
            self.request.session.flash(u'入力されていません')

        return {
            'form':form,
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
