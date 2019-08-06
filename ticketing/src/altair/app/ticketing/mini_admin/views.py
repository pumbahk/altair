# -*- coding:utf-8 -*-
from altair.app.ticketing.core.models import ReportSetting
from altair.app.ticketing.events.lots.api import get_lot_entry_status
from altair.app.ticketing.events.sales_reports.forms import (
    SalesReportForm,
    SalesReportDownloadForm,
    ReportSettingForm,
)
from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_defaults
from webob.multidict import MultiDict


@view_defaults(decorator=with_bootstrap,
               renderer='altair.app.ticketing:templates/mini_admin/index.html',
               permission="mini_admin_viewer")
class MiniAdminView(BaseView):
    def __init__(self, context, request):
        super(MiniAdminView, self).__init__(context, request)

    @lbr_view_config(route_name='mini_admin.index')
    def index(self):
        return {
            'operator_group': self.context.user.group
        }


@view_defaults(decorator=with_bootstrap,
               renderer='altair.app.ticketing:templates/mini_admin/report.html',
               permission='mini_admin_viewer')
class MiniAdminReportView(BaseView):

    def __init__(self, context, request):
        super(MiniAdminReportView, self).__init__(context, request)

    def flash_limited_err_msg(self, limited_errors):
        for msg in limited_errors:
            self.request.session.flash(msg)

    @lbr_view_config(route_name='mini_admin.report')
    def mini_admin_report(self):
        event = self.context.event
        form = SalesReportForm(self.request.params, event_id=event.id)
        download_form = SalesReportDownloadForm(self.request.params, event_id=event.id)
        event_total_reporter = None
        performance_total_reporter = None

        form.validate()
        self.flash_limited_err_msg(form.limited_from.errors)
        if not form.limited_from.errors:
            event_total_reporter = SalesTotalReporter(self.request, form, self.context.organization)
            performance_total_reporter = SalesTotalReporter(self.request, form, self.context.organization, group_by='Performance')

        return {'event':event,
                'form_report_setting':ReportSettingForm(MultiDict(event_id=event.id), context=self.context),
                'report_settings':ReportSetting.filter_by(event_id=event.id).all(),
                'event_total_reporter':event_total_reporter,
                'performance_total_reporter':performance_total_reporter,
                'form':form,
                'download_form':download_form
                }


@view_defaults(decorator=with_bootstrap,
               renderer='altair.app.ticketing:templates/mini_admin/lot_report.html',
               permission='mini_admin_viewer')
class MiniAdminLotView(BaseView):

    def __init__(self, context, request):
        super(MiniAdminLotView, self).__init__(context, request)

    @lbr_view_config(route_name='mini_admin.lot.report')
    def show_lot_report(self):
        lot = self.context.lot
        if not lot:  # 抽選が存在しない
            raise HTTPNotFound

        # オペレータに紐付いていない抽選のため表示しない
        if not self.context.exist_operator_event():
            raise HTTPNotFound

        return dict(
            lot=lot,
            lot_status=get_lot_entry_status(lot, self.request)
        )
