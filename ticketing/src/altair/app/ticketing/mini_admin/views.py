# -*- coding:utf-8 -*-
from altair.app.ticketing.core.models import ReportSetting
from altair.app.ticketing.events.lots.api import get_lot_entry_status
from altair.app.ticketing.events.lots.models import CSVExporter
from altair.app.ticketing.events.sales_reports.forms import (
    SalesReportForm,
    SalesReportDownloadForm,
    ReportSettingForm,
)
from altair.app.ticketing.events.sales_reports.reports import PerformanceReporter
from altair.app.ticketing.events.sales_reports.reports import SalesTotalReporter
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.lots.models import LotEntry
from altair.app.ticketing.views import BaseView
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.sqlahelper import get_db_session
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config, view_defaults
from webob.multidict import MultiDict

from .forms import MiniAdminOrderSearchForm
from ..orders.api import (
    get_patterns_info
)
from ..orders.forms import OrderForm
from ..orders.views import OrderBaseView


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
               permission='mini_admin_viewer')
class MiniAdminReportView(BaseView):

    def __init__(self, context, request):
        super(MiniAdminReportView, self).__init__(context, request)

    def flash_limited_err_msg(self, limited_errors):
        for msg in limited_errors:
            self.request.session.flash(msg)

    @lbr_view_config(route_name='mini_admin.event.report',
                     renderer='altair.app.ticketing:templates/mini_admin/report.html')
    def mini_admin_event_report(self):
        event = self.context.event
        form = SalesReportForm(self.request.params, event_id=event.id)
        download_form = SalesReportDownloadForm(self.request.params, event_id=event.id)
        event_total_reporter = None
        performance_total_reporter = None

        form.validate()
        self.flash_limited_err_msg(form.limited_from.errors)
        if not form.limited_from.errors:
            event_total_reporter = SalesTotalReporter(self.request, form, self.context.organization)
            performance_total_reporter = SalesTotalReporter(self.request, form, self.context.organization,
                                                            group_by='Performance')

        return {'event': event,
                'form_report_setting': ReportSettingForm(MultiDict(event_id=event.id), context=self.context),
                'report_settings': ReportSetting.filter_by(event_id=event.id).all(),
                'event_total_reporter': event_total_reporter,
                'performance_total_reporter': performance_total_reporter,
                'form': form,
                'download_form': download_form
                }

    @lbr_view_config(route_name='mini_admin.performance.report',
                     renderer='altair.app.ticketing:templates/mini_admin/report_performance.html')
    def mini_admin_performance_report(self):
        performance = self.context.performance
        form = SalesReportForm(self.request.params, performance_id=performance.id)
        download_form = SalesReportDownloadForm(self.request.params, performance_id=performance.id)
        performance_reporter = None

        form.validate()
        self.flash_limited_err_msg(form.limited_from.errors)
        if not form.limited_from.errors:
            performance_reporter = PerformanceReporter(self.request, form, performance)

        return {
            'form_report_setting': ReportSettingForm(MultiDict(performance_id=performance.id),
                                                     context=self.context),
            'report_settings': ReportSetting.filter_by(performance_id=performance.id).all(),
            'performance_reporter': performance_reporter,
            'performance': performance,
            'form': form,
            'download_form': download_form
        }


@view_defaults(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/mini_admin/order_search.html',
               permission='mini_admin_viewer')
class MiniAdminOrderSearchView(OrderBaseView):

    @view_config(route_name='mini_admin.order_search')
    def mini_admin_order_search(self):
        request = self.request
        patterns = get_patterns_info(request)
        organization_id = request.context.organization.id
        params = MultiDict(request.POST)
        params["order_no"] = " ".join(request.POST.getall("order_no"))
        event_id = request.matchdict['event_id']

        if not event_id:
            raise HTTPNotFound

        related_event = [operator_event for operator_event in self.context.user.group.events if
                         str(operator_event.id) == event_id]

        # オペレータに紐付いたイベントでない場合は404にする
        if not related_event:
            raise HTTPNotFound

        form_search = MiniAdminOrderSearchForm(params, organization_id=organization_id, event_id=event_id)

        return {
            'form': OrderForm(context=self.context),
            'form_search': form_search,
            'endpoints': self.endpoints,
            'patterns': patterns
        }


@view_defaults(decorator=with_bootstrap,
               route_name='mini_admin.lot.report',
               permission='mini_admin_viewer')
class MiniAdminLotView(BaseView):

    def __init__(self, context, request):
        super(MiniAdminLotView, self).__init__(context, request)

    @lbr_view_config(request_method='GET', renderer='altair.app.ticketing:templates/mini_admin/lot_report.html')
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

    @lbr_view_config(request_method='POST', renderer='csv')
    def export_entries(self):
        lot = self.context.lot
        if not lot:  # 抽選が存在しない
            raise HTTPNotFound

        # オペレータに紐付いていない抽選のため表示しない
        if not self.context.exist_operator_event():
            raise HTTPNotFound

        slave_session = get_db_session(self.request, name="slave")
        condition = LotEntry.id.isnot(None)
        entries = CSVExporter(slave_session, lot.id, condition)

        if entries.all() and not entries.all()[0]:
            self.request.session.flash(u'対象となる申込が1件もないため、ダウンロード出来ませんでした')
            return HTTPFound(location=self.request.route_url('mini_admin.lot.report', lot_id=lot.id))

        filename = 'lot-{0.id}.csv'.format(lot)
        self.request.response.content_type = 'text/plain;charset=Shift_JIS'
        self.request.response.content_disposition = 'attachment; filename=' + filename
        return dict(data=list(entries), encoding='sjis', filename=filename)
