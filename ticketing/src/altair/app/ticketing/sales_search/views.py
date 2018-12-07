# -*- coding:utf-8 -*-
import webhelpers.paginate as paginate
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.pyramid_dynamic_renderer import lbr_view_config

from .forms import SalesSearchForm


class SalesSearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.index')
    def index(self):
        sales_report_operators = self.context.get_sales_report_operators()
        form = SalesSearchForm(formdata=self.request.params, obj=None, prefix='',
                               sales_report_operators=sales_report_operators)
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

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.download', request_method="POST")
    def download(self):
        form = SalesSearchForm(self.request.POST)
        sales_segments = self.context.search(form)
        return dict(
            form=form,
            sales_segments=sales_segments,
            helper=self.context.helper
        )
