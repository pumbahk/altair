 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap


import webhelpers.paginate as paginate

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class Admin(BaseView):

    @view_config(route_name='admin.index', renderer='ticketing:templates/admin/index.html')
    def index(self):
        return dict()

    @view_config(route_name='admin.client', renderer='ticketing:templates/admin/client.html')
    def client(self):
        return dict()

    @view_config(route_name='admin.super', renderer='ticketing:templates/admin/client.html')
    def super(self):
        return dict()