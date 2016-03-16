# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
import urllib

import webhelpers.paginate as paginate
from webob.multidict import MultiDict
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.url import route_path
from sqlalchemy.sql import func
from wtforms.validators import Optional

from altair.app.ticketing.models import merge_session_with_post
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, ReportSetting, ReportRecipient
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.events.sales_reports.forms import (
    SalesReportSearchForm,
    SalesReportForm,
    ReportSettingForm,
    OnlyEmailCheckForm,
    NumberOfPerformanceReportExportForm,
    )

from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter, PerformanceReporter, EventReporter, ExportableReporter, sendmail, ExportNumberOfPerformanceReporter
from altair.app.ticketing.events.sales_reports.exceptions import ReportSettingValidationError
from altair.app.ticketing.utils import get_safe_filename

logger = logging.getLogger(__name__)


@view_defaults(decorator=with_bootstrap, permission='sales_viewer')
class SalesReports(BaseView):

    @view_config(route_name='sales_reports.index', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/index.html')
    def index(self):
        form = SalesReportSearchForm()
        now = datetime.now()
        if not form.event_from.data:
            form.event_from.process_data(now.replace(hour=0, minute=0, second=0) + timedelta(days=-31))
        if not form.event_to.data:
            form.event_to.process_data(now.replace(hour=23, minute=59, second=59) + timedelta(days=365))

        return {
            'form':form,
            'export_form':NumberOfPerformanceReportExportForm(),
            }

    @view_config(route_name='sales_reports.index', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/index.html')
    def index_post(self):
        form = SalesReportSearchForm(self.request.params)
        if form.validate():
            event_total_reporter = SalesTotalReporter(self.request, form, self.context.organization)
            return {
                'form':form,
                'event_total_reporter':event_total_reporter,
                'export_form':NumberOfPerformanceReportExportForm(),
                }
        else:
            return {
                'form':form,
                'export_form':NumberOfPerformanceReportExportForm(),
                }

    @view_config(route_name='sales_reports.event', renderer='altair.app.ticketing:templates/sales_reports/event.html')
    def event(self):
        event = self.context.event
        form = SalesReportForm(self.request.params, event_id=event.id)
        event_total_reporter = SalesTotalReporter(self.request, form, self.context.organization)
        performance_total_reporter = SalesTotalReporter(self.request, form, self.context.organization, group_by='Performance')

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
            'performance_reporter':PerformanceReporter(self.request, form, performance),
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
            form.recipient.data = ', '.join([rs.format_emails() for rs in report_settings])
        if not form.subject.data:
            form.subject.data = u'[売上レポート|%s] %s' % (self.context.user.organization.name, subject)

        return {
            'form':form,
            }

    @view_config(route_name='sales_reports.export')
    def get_exported(self):
        event_id = long(self.request.params.get('event_id') or 0)
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        
        render_param = dict(reporter=ExportableReporter(self.request, event), encoding="cp932")
        r = render_to_response('altair.app.ticketing:templates/sales_reports/export.txt', render_param, request=self.request)
        if(self.request.params.get('view')):
            r.headers['Content-Type'] = 'text/plain'
            return r
        filename = u"%s.csv" % get_safe_filename(event.title)
        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(filename.encode("utf-8")))
        ]
        return Response(r.text.encode('cp932'), headers=headers)

    @view_config(route_name='sales_reports.export_number_of_performance')
    def export_number_of_performance(self):
        form = NumberOfPerformanceReportExportForm(self.request.params)
        if not form.validate():
            for field, errors in form.errors.items():
                for err in errors:
                    self.request.session.flash(err)
            return HTTPFound(self.request.route_url('sales_reports.index'))

        render_param = dict(reporter=ExportNumberOfPerformanceReporter(self.request, form.export_time_from.data, form.export_time_to.data), encoding="cp932")
        r = render_to_response('altair.app.ticketing:templates/sales_reports/number_of_performance_export.txt', render_param, request=self.request)
        if self.request.params.get('view'):
            r.headers['Content-Type'] = 'text/plain'
            return r
        filename = u"販売公演数{0}.csv".format(get_safe_filename(form.export_time_from.data.strftime('%Y-%m-%d')))
        headers = [
            ('Content-Type', 'application/octet-stream; charset=utf-8'),
            ('Content-Disposition', "attachment; filename*=utf-8''%s" % urllib.quote(filename.encode("utf-8")))
        ]
        return Response(r.text.encode('cp932'), headers=headers)

    @view_config(route_name='sales_reports.export_xml')
    def get_exported_xml(self):
        event_id = long(self.request.params.get('event_id') or 0)
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            raise HTTPNotFound('event id %d is not found' % event_id)
        
        reporter = ExportableReporter(self.request, event)
        return Response(reporter.get_xml(), headers=[ ('Content-Type', 'text/xml') ])

    @view_config(route_name='sales_reports.mail_body')
    def mail_body(self):
        event_id = long(self.request.params.get('event_id') or 0)
        performance_id = long(self.request.params.get('performance_id') or 0)

        form = SalesReportForm(self.request.params)
        form.subject.validators = [Optional()]
        form.recipient.validators = [Optional()]
        if form.validate():
            if performance_id:
                performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
                if performance is None:
                    raise HTTPNotFound('performance id %d is not found' % performance_id)

                render_param = dict(performance_reporter=PerformanceReporter(self.request, form, performance))
                return render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param, request=self.request)
            elif event_id:
                event = Event.get(event_id, organization_id=self.context.user.organization_id)
                if event is None:
                    raise HTTPNotFound('event id %d is not found' % event_id)

                render_param = dict(event_reporter=EventReporter(self.request, form, event))
                return render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param, request=self.request)
            else:
                raise HTTPNotFound('event and performance id is not found')
        else:
            logger.debug('mail_body validation error:{0}'.format(form.errors))
            return Response()

    @view_config(route_name='sales_reports.send_mail', renderer='altair.app.ticketing:templates/sales_reports/preview.html')
    def send_mail(self):
        event_id = long(self.request.params.get('event_id') or 0)
        performance_id = long(self.request.params.get('performance_id') or 0)

        form = SalesReportForm(self.request.params)
        if form.validate():
            if performance_id:
                performance = Performance.get(performance_id, organization_id=self.context.user.organization_id)
                if performance is None:
                    raise HTTPNotFound('performance id %d is not found' % performance_id)

                render_param = dict(performance_reporter=PerformanceReporter(self.request, form, performance))
                html = render_to_response('altair.app.ticketing:templates/sales_reports/performance_mail.html', render_param, request=self.request)
            elif event_id:
                event = Event.get(event_id, organization_id=self.context.user.organization_id)
                if event is None:
                    raise HTTPNotFound('event id %d is not found' % event_id)

                render_param = dict(event_reporter=EventReporter(self.request, form, event))
                html = render_to_response('altair.app.ticketing:templates/sales_reports/event_mail.html', render_param, request=self.request)
            else:
                raise HTTPNotFound('event and performance id is not found')

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

    def _save_report_setting(self, report_setting=None):
        if report_setting is None:
            report_setting = ReportSetting()

        form = ReportSettingForm(self.request.POST, context=self.context)
        if not form.validate():
            raise ReportSettingValidationError(form=form)

        num = 0
        report_setting.recipients = []
        for line in form.recipients.data.splitlines():
            num += 1
            row = line.split(',')

            recipient = ReportRecipient()

            # メアドのみ
            if len(row) == 1:
                recipient.name = ""
                recipient.email = row[0].strip()

            # 名前とメアド
            elif len(row) == 2:
                recipient.name = row[0].strip()
                recipient.email = row[1].strip()

            recipient.organization_id = self.context.organization.id
            report_setting.recipients.append(recipient)

        report_setting.frequency = form.frequency.data
        report_setting.event_id = form.event_id.data
        report_setting.day_of_week = form.day_of_week.data
        report_setting.time = form.time.data
        report_setting.start_on = form.start_on.data
        report_setting.end_on = form.end_on.data
        report_setting.performance_id = form.performance_id.data
        report_setting.period = form.period.data
        report_setting.report_type = form.report_type.data

        report_setting.save()

    @view_config(route_name='report_settings.new', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def new_xhr(self):
        return {
            'form': ReportSettingForm(self.request.params, context=self.context),
            'action': self.request.path,
            }

    @view_config(route_name='report_settings.new', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def new_post(self):
        try:
            self._save_report_setting()
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        except ReportSettingValidationError as e:
            return {
                'form':e.form,
                'action': self.request.path,
                }
        self.request.session.flash(u'レポート送信設定を保存しました')

    @view_config(route_name='report_settings.edit', request_method='GET', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def edit_xhr(self):
        form = ReportSettingForm(obj=self.context.report_setting, context=self.context)
        recipient_list = []
        for recipient in self.context.report_setting.recipients:
            if recipient.name:
                recipient_list.append(recipient.name + "," + recipient.email)
            else:
                recipient_list.append(recipient.email)
        form.recipients.data = "\n".join(recipient_list)

        return {
            'form': form,
            'action': self.request.path,
            }

    @view_config(route_name='report_settings.edit', request_method='POST', renderer='altair.app.ticketing:templates/sales_reports/_form.html', xhr=True)
    def edit_post_xhr(self):
        try:
            self._save_report_setting(self.context.report_setting)
            self.request.session.flash(u'レポート送信設定を保存しました')
            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)
        except ReportSettingValidationError as e:
            return {
                'form':e.form,
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
            remove_candidates = set(report_setting.recipients)
            for c in remove_candidates:
                if len(c.lot_entry_report_settings) == 0 and len([s for s in c.settings if s.id != report_setting.id]) == 0:
                    logger.info(u'remove no reference recipient id={} name={} email={}'.format(c.id, c.name, c.email))
                    c.delete()
            report_setting.delete()
            self.request.session.flash(u'選択したレポート送信設定を削除しました')
        except Exception as e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=location)

        return HTTPFound(location=location)
