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
from ticketing.core.models import Event, ReportSetting
from ticketing.core.models import Performance
from ticketing.events.sales_reports.forms import SalesReportForm, SalesReportMailForm
from ticketing.events.sales_reports.reports import SalesTotalReporter, PerformanceReporter, EventReporter, sendmail

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReports(BaseView):

    @view_config(route_name='sales_reports.index', renderer='ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportForm(self.request.params)
        event_total_reporter = SalesTotalReporter(form, self.context.organization)

        return {
            'form':form,
            'event_total_reporter':event_total_reporter,
        }

    @view_config(route_name='sales_reports.event', renderer='ticketing:templates/sales_reports/event.html')
    def event(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        form = SalesReportForm(self.request.params, event_id=event_id)
        event_total_reporter = SalesTotalReporter(form, self.context.organization)
        performance_total_reporter = SalesTotalReporter(form, self.context.organization, group_by='Performance')

        return {
            'form':form,
            'form_report_mail':SalesReportMailForm(organization_id=self.context.user.organization_id, event_id=event_id),
            'report_settings':ReportSetting.filter_by(event_id=event_id).all(),
            'event_total_reporter':event_total_reporter,
            'performance_total_reporter':performance_total_reporter
        }

    @view_config(route_name='sales_reports.performance', renderer='ticketing:templates/sales_reports/performance.html')
    def performance(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            raise HTTPNotFound('performance id %d is not found' % performance_id)

        form = SalesReportForm(self.request.params, performance_id=performance_id)
        return {
            'performance_reporter':PerformanceReporter(form, performance),
        }

    @view_config(route_name='sales_reports.preview', renderer='ticketing:templates/sales_reports/preview.html')
    def preview(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        form = SalesReportForm(self.request.params, event_id=event_id)
        if not form.recipient.data:
            form.recipient.data = ','.join([rs.recipient for rs in event.report_setting])
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
        return {
            'event_reporter':EventReporter(form, event),
        }

    @view_config(route_name='sales_reports.send_mail', renderer='ticketing:templates/sales_reports/preview.html')
    def send_mail(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
     
        form = SalesReportForm(self.request.params, event_id=event_id)
        if form.validate():
            settings = self.request.registry.settings
            recipient = form.recipient.data
            subject = form.subject.data or u'[売上レポート] %s' % event.title
            render_param = {
                'event_reporter':EventReporter(form, event),
            }
            html = render_to_response('ticketing:templates/sales_reports/mail_body.html', render_param, request=self.request)
            if sendmail(settings, recipient, subject, html):
                self.request.session.flash(u'レポートメールを送信しました')
            else:
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
