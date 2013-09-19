# -*- coding: utf-8 -*-

import logging

import webhelpers.paginate as paginate
from webob.multidict import MultiDict
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func

from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, ReportSetting
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.events.sales_reports.forms import SalesReportForm, SalesReportMailForm
from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter, PerformanceReporter, EventReporter, sendmail

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReports(BaseView):

    @view_config(route_name='sales_reports.index', renderer='altair.app.ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportForm(self.request.params)
        event_total_reporter = SalesTotalReporter(form, self.context.organization)

        return {
            'form':form,
            'event_total_reporter':event_total_reporter,
        }

    @view_config(route_name='sales_reports.event', renderer='altair.app.ticketing:templates/sales_reports/event.html')
    def event(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)

        form = SalesReportForm(self.request.params, event_id=event_id)
        event_total_reporter = SalesTotalReporter(form, self.context.organization)
        performance_total_reporter = SalesTotalReporter(form, self.context.organization, group_by='Performance')

        return {
            'event':event,
            'form_report_mail':SalesReportMailForm(MultiDict(event_id=event_id), organization_id=self.context.user.organization_id),
            'report_settings':ReportSetting.filter_by(event_id=event_id).all(),
            'event_total_reporter':event_total_reporter,
            'performance_total_reporter':performance_total_reporter
        }

    @view_config(route_name='sales_reports.performance', renderer='altair.app.ticketing:templates/sales_reports/performance.html')
    def performance(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id, self.context.user.organization_id)
        if performance is None:
            raise HTTPNotFound('performance id %d is not found' % performance_id)

        form = SalesReportForm(self.request.params, performance_id=performance_id)
        return {
            'form_report_mail':SalesReportMailForm(MultiDict(performance_id=performance_id), organization_id=self.context.user.organization_id),
            'report_settings':ReportSetting.filter_by(performance_id=performance_id).all(),
            'performance_reporter':PerformanceReporter(form, performance),
        }

    @view_config(route_name='sales_reports.preview', renderer='altair.app.ticketing:templates/sales_reports/preview.html')
    def preview(self):
        event_id = int(self.request.params.get('event_id') or 0)
        performance_id = int(self.request.params.get('performance_id') or 0)

        if performance_id:
            performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
            if performance is None:
                raise HTTPNotFound('performance id %d is not found' % performance_id)
            report_settings = performance.report_settings
            subject = u'%s (開催日:%s)' % (performance.name, performance.start_on.strftime('%Y-%m-%d %H:%M'))
        elif event_id:
            event = Event.get(event_id, organization_id=self.context.user.organization_id)
            if event is None:
                raise HTTPNotFound('event id %d is not found' % event_id)
            report_settings = event.report_settings
            subject = event.title
        else:
            raise HTTPNotFound('event and performance id is not found')

        form = SalesReportForm(self.request.params)
        if not form.recipient.data:
            form.recipient.data = ', '.join([rs.recipient for rs in report_settings])
        if not form.subject.data:
            form.subject.data = u'[売上レポート|%s] %s' % (self.context.user.organization.name, subject)

        return {
            'form':form,
        }

    @view_config(route_name='sales_reports.mail_body')
    def mail_body(self):
        event_id = int(self.request.params.get('event_id') or 0)
        performance_id = int(self.request.params.get('performance_id') or 0)

        form = SalesReportForm(self.request.params)
        if performance_id:
            performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
            if performance is None:
                raise HTTPNotFound('performance id %d is not found' % performance_id)
            render_param = dict(performance_reporter=PerformanceReporter(form, performance))
            return render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param, request=self.request)
        elif event_id:
            event = Event.get(event_id, organization_id=self.context.user.organization_id)
            if event is None:
                raise HTTPNotFound('event id %d is not found' % event_id)
            render_param = dict(event_reporter=EventReporter(form, event))
            return render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param, request=self.request)
        else:
            raise HTTPNotFound('event and performance id is not found')

    @view_config(route_name='sales_reports.send_mail', renderer='altair.app.ticketing:templates/sales_reports/preview.html')
    def send_mail(self):
        event_id = int(self.request.params.get('event_id') or 0)
        performance_id = int(self.request.params.get('performance_id') or 0)

        if performance_id:
            performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
            if performance is None:
                raise HTTPNotFound('performance id %d is not found' % performance_id)
            form = SalesReportForm(self.request.params)
        elif event_id:
            event = Event.get(event_id, organization_id=self.context.user.organization_id)
            if event is None:
                raise HTTPNotFound('event id %d is not found' % event_id)
            form = SalesReportForm(self.request.params)
        else:
            raise HTTPNotFound('event and performance id is not found')

        if form.validate():
            if performance_id:
                render_param = {
                    'performance_reporter':PerformanceReporter(form, performance)
                }
                html = render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param, request=self.request)
            elif event_id:
                render_param = {
                    'event_reporter':EventReporter(form, event)
                }
                html = render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param, request=self.request)

            settings = self.request.registry.settings
            recipient = form.recipient.data
            subject = form.subject.data
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

    @view_config(route_name='sales_reports.mail.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/_form.html')
    def new_post(self):
        f = SalesReportMailForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            report_mail = merge_session_with_post(ReportSetting(), f.data)
            report_mail.save()
            self.request.session.flash(u'新規メール送信先を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
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

        if report_setting.performance_id:
            location = route_path('sales_reports.performance', self.request, performance_id=report_setting.performance_id)
        else:
            location = route_path('sales_reports.event', self.request, event_id=report_setting.event.id)
        try:
            report_setting.delete()
            self.request.session.flash(u'選択した送信先を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
