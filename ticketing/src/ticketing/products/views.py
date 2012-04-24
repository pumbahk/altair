# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView

from ticketing.fanstatic import with_bootstrap

@view_defaults(decorator=with_bootstrap)
class Products(BaseView):

    @view_config(route_name='products.index', renderer='ticketing:templates/products/index.html')
    def index(self):
        return {}

@view_defaults(decorator=with_bootstrap)
class ProductSegments(BaseView):
    @view_config(route_name='products.sales_segments', renderer='ticketing:templates/products_segments/index.html')
    def index(self):
        return {}