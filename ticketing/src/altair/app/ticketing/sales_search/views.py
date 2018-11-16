# -*- coding:utf-8 -*-
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.fanstatic import with_bootstrap
from .forms import SalesSearchForm


class SalesSearchView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.index')
    def show(self):
        form = SalesSearchForm()
        return dict(
            form=form
        )

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.search', request_method="POST")
    def search(self):
        form = SalesSearchForm(self.request.POST)
        result = self.context.search(form)

        return dict(
            form=form,
            result=result
        )

    @lbr_view_config(decorator=with_bootstrap, renderer='altair.app.ticketing:templates/sales_search/index.html',
                     route_name='sales_search.download', request_method="POST")
    def download(self):
        form = SalesSearchForm(self.request.POST)
        result = self.context.search(form)
        return dict(
            form=form,
            result=result
        )
