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
    NumberOfPerformanceReportExportForm,
    )

from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter, PerformanceReporter, EventReporter, ExportableReporter, sendmail, ExportNumberOfPerformanceReporter
from altair.app.ticketing.events.sales_reports.exceptions import ReportSettingValidationError
from altair.app.ticketing.utils import get_safe_filename
from .forms import PrintedReportSettingForm, PrintedReportRecipientForm

logger = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap, permission='sales_viewer'
        , renderer='altair.app.ticketing:templates/printed_reports/edit.html')
class PrintedReports(BaseView):

    @view_config(route_name='printed_reports.edit', request_method='GET')
    @view_config(route_name='printed_reports.recipients_update', request_method='GET')
    def edit_get(self):
        return dict(
            event=self.context.event,
            report_setting=self.context.printed_report_setting,
            report_setting_form=PrintedReportSettingForm(),
            recipients_form=self.context.get_printed_report_recipients_form(),
        )

    @view_config(route_name='printed_reports.report_setting_update', request_method='POST')
    def report_setting_update(self):
        
        form=self.context.update_printed_report_setting()

        message=""
        if form.validate():
            self.request.session.flash(u"発券進捗メールの送信時刻を変更しました。")
        else:
            message=u"送信期間が正しく入力されていません"

        return dict(
            message=message,
            event=self.context.event,
            report_setting=self.context.printed_report_setting,
            report_setting_form=PrintedReportSettingForm(),
            recipients_form=self.context.get_printed_report_recipients_form(),
        )

    @view_config(route_name='printed_reports.recipients_update', request_method='POST')
    def recipient_update(self):
        self.context.update_recipient()
        self.request.session.flash(u"発券進捗メールの送信先を変更しました。")
        return dict(
            event=self.context.event,
            report_setting=self.context.printed_report_setting,
            report_setting_form=PrintedReportSettingForm(),
            recipients_form=self.context.get_printed_report_recipients_form(),
        )
