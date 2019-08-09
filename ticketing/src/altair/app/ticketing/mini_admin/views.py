# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.models import Event
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
from altair.sqlahelper import get_db_session
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config, view_defaults
from webob.multidict import MultiDict

from ..orders.api import (
    get_patterns_info
)
from .forms import OrderSearchForm
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


@view_defaults(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/mini_admin/order_search.html',
               permission='mini_admin_viewer')
class MiniAdminOrderSearchView(OrderBaseView):

    @view_config(route_name='mini_admin.order_search')
    def mini_admin_order_search(self):
        request = self.request
        patterns = get_patterns_info(request)
        slave_session = get_db_session(request, name="slave")
        organization_id = request.context.organization.id

        params = MultiDict(request.POST)
        params["order_no"] = " ".join(request.POST.getall("order_no"))
        event_id = request.matchdict['event_id']
        if event_id:
            event = slave_session.query(Event).filter(Event.id == event_id).first()
            form_search = OrderSearchForm(params, organization_id=organization_id, event_id=event_id)
        else:
            raise HTTPNotFound

        orders = None
        page = int(request.GET.get('page', 0))

        from ..orders.download import OrderSummary
        if form_search.validate():
            query = OrderSummary(self.request,
                                 slave_session,
                                 organization_id,
                                 condition=form_search)
        else:
            return {
                'form': OrderForm(context=self.context),
                'form_search': form_search,
                'orders': orders,
                'page': page,
                'endpoints': self.endpoints,
                'patterns': patterns
            }

        if request.params.get('action') == 'checked':
            checked_orders = [o.lstrip('o:') for o in request.session.get('orders', []) if o.startswith('o:')]
            query.target_order_ids = checked_orders

        count = query.count()
        orders = paginate.Page(
            query,
            page=page,
            item_count=count,
            items_per_page=40,
            url=paginate.PageURL_WebOb(request)
        )

        return {
            'form': OrderForm(context=self.context),
            'form_search': form_search,
            'orders': orders,
            'page': page,
            'endpoints': self.endpoints,
            'event': event,
            'patterns': patterns
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
