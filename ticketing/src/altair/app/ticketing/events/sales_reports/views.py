# -*- coding: utf-8 -*-

import json
from datetime import datetime
import logging

import webhelpers.paginate as paginate
from webob.multidict import MultiDict
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.url import route_path
from sqlalchemy.sql import func

from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, ReportSetting
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.events.sales_reports.forms import SalesReportForm, ReportSettingForm
from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter, PerformanceReporter, EventReporter, sendmail

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class SalesReports(BaseView):

    @view_config(route_name='sales_reports.index', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportForm()
        form.recent_report.data = True
        event_total_reporter = SalesTotalReporter(form, self.context.organization)

        return {
            'form':form,
            'event_total_reporter':event_total_reporter,
            }

    @view_config(route_name='sales_reports.index', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/index.html')
    def index_post(self):
        form = SalesReportForm(self.request.params)
        form.recent_report.data = False
        event_total_reporter = SalesTotalReporter(form, self.context.organization)

        return {
            'form':form,
            'event_total_reporter':event_total_reporter,
            }

    @view_config(route_name='sales_reports.index_all', renderer='altair.app.ticketing:templates/sales_reports/index_all.html')
    def index_all(self):
        form = SalesReportForm(self.request.params)
        form.recent_report.data = False
        event_total_reporter = SalesTotalReporter(form, self.context.organization)

        return {
            'form':form,
            'event_total_reporter':event_total_reporter,
            }

    @view_config(route_name='sales_reports.event', renderer='altair.app.ticketing:templates/sales_reports/event.html')
    def event(self):
        event = self.context.event

        form = SalesReportForm(self.request.params, event_id=event.id)
        event_total_reporter = SalesTotalReporter(form, self.context.organization)
        performance_total_reporter = SalesTotalReporter(form, self.context.organization, group_by='Performance')

        return {
            'event':event,
            'form_report_setting':ReportSettingForm(MultiDict(event_id=event.id), context=self.context),
            'report_settings':ReportSetting.filter_by(event_id=event.id).all(),
            'event_total_reporter':event_total_reporter,
            'performance_total_reporter':performance_total_reporter
            }

    @view_config(route_name='sales_reports.performance', renderer='altair.app.ticketing:templates/sales_reports/performance.html')
    def performance(self):
        performance = self.context.performance

        form = SalesReportForm(self.request.params, performance_id=performance.id)
        return {
            'form_report_setting':ReportSettingForm(MultiDict(performance_id=performance.id), context=self.context),
            'report_settings':ReportSetting.filter_by(performance_id=performance.id).all(),
            'performance_reporter':PerformanceReporter(form, performance),
            }

    @view_config(route_name='sales_reports.preview', renderer='altair.app.ticketing:templates/sales_reports/preview.html')
    def preview(self):
        event_id = long(self.request.params.get('event_id') or 0)
        performance_id = long(self.request.params.get('performance_id') or 0)

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
        event_id = long(self.request.params.get('event_id') or 0)
        performance_id = long(self.request.params.get('performance_id') or 0)

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
        event_id = long(self.request.params.get('event_id') or 0)
        performance_id = long(self.request.params.get('performance_id') or 0)

        if performance_id:
            performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
            if performance is None:
                raise HTTPNotFound('performance id %d is not found' % performance_id)
        elif event_id:
            event = Event.get(event_id, organization_id=self.context.user.organization_id)
            if event is None:
                raise HTTPNotFound('event id %d is not found' % event_id)
        else:
            raise HTTPNotFound('event and performance id is not found')

        form = SalesReportForm(self.request.params)
        if form.validate():
            if performance_id:
                render_param = dict(performance_reporter=PerformanceReporter(form, performance))
                html = render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param, request=self.request)
            elif event_id:
                render_param = dict(event_reporter=EventReporter(form, event))
                html = render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param, request=self.request)

            settings = self.request.registry.settings
            recipient = form.recipient.data
            subject = form.subject.data
            if sendmail(settings, recipient, subject, html):
                self.request.session.flash(u'レポートを送信しました')
            else:
                self.request.session.flash(u'レポート送信に失敗しました')
        else:
            self.request.session.flash(u'入力されていません')

        return {
            'form':form,
            }


@view_defaults(decorator=with_bootstrap, permission='sales_editor')
class ReportSettings(BaseView):

    @view_config(route_name='report_settings.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def new_xhr(self):
        return {
            'form': ReportSettingForm(self.request.params, context=self.context),
            'action': self.request.path,
            }

    @view_config(route_name='report_settings.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def new_post(self):
        f = ReportSettingForm(self.request.POST, context=self.context)
        if f.validate():
            report_mail = merge_session_with_post(ReportSetting(), f.data)
            report_mail.save()
            self.request.session.flash(u'レポート送信設定を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form':f,
                'action': self.request.path,
                }

    @view_config(route_name='report_settings.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def edit_xhr(self):
        return {
            'form': ReportSettingForm(obj=self.context.report_setting, context=self.context),
            'action': self.request.path,
            }

    def _edit_post(self):
        f = ReportSettingForm(self.request.POST, context=self.context)
        if not f.validate():
            return f
        report_setting = self.context.report_setting
        report_setting = merge_session_with_post(report_setting, f.data)
        report_setting.save()

        self.request.session.flash(u'レポート送信設定を保存しました')
        return None

    @view_config(route_name='report_settings.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/_form.html')
    def edit_post_xhr(self):
        f = self._edit_post()
        if f is None:
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        else:
            return {
                'form': f,
                'action': self.request.path,
                }

    @view_config(route_name='report_settings.delete')
    def delete(self):
        report_setting = self.context.report_setting

        if report_setting.performance_id:
            location = route_path('sales_reports.performance', self.request, performance_id=report_setting.performance_id)
        else:
            location = route_path('sales_reports.event', self.request, event_id=report_setting.event.id)

        try:
            report_setting.delete()
            self.request.session.flash(u'選択したレポート送信設定を削除しました')
        except Exception as e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
