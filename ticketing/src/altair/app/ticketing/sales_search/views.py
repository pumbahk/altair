# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.pyramid_dynamic_renderer import lbr_view_config
from pyramid.httpexceptions import HTTPFound

from .exporter import CSVExporter
from .forms import SalesSearchForm


class SalesSearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.index')
    def index(self):
        sales_report_operators = self.context.get_sales_report_operators()
        sales_report_operators.insert(0, (0, u"全てを選択"))
        form = SalesSearchForm(formdata=self.request.params, obj=None, prefix='',
                               sales_report_operators=sales_report_operators)
        if not self.context.check_sales_term(form):
            self.request.session.flash(u"期間指定の場合は、日付を指定してください")
            return dict(
                form=form,
                sales_segments=None,
                helper=self.context.helper
            )

        sales_segments = self.context.search(form)

        sales_segments = paginate.Page(
            sales_segments,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return dict(
            form=form,
            sales_segments=sales_segments,
            helper=self.context.helper
        )

    @lbr_view_config(route_name='sales_search.download', renderer='csv')
    def download(self):
        sales_report_operators = self.context.get_sales_report_operators()
        form = SalesSearchForm(formdata=self.request.params, obj=None, prefix='',
                               sales_report_operators=sales_report_operators)
        if not self.context.check_sales_term(form):
            self.request.session.flash(u"期間指定の場合は、日付を指定してください")
            return HTTPFound(self.request.route_path("sales_search.index"))

        sales_segments = self.context.search(form)
        if not sales_segments:
            self.request.session.flash(u"ダウンロードする結果がありません")
            return HTTPFound(self.request.route_path("sales_search.index"))

        exporter = CSVExporter(sales_segments)

        filename = u"SalesSearchReport.csv"
        self.request.response.content_type = u"text/plain;charset=Shift_JIS"
        self.request.response.content_disposition = u"attachment; filename={0}".format(filename)

        return dict(data=list(exporter),
                    encoding='sjis',
                    filename=filename)
