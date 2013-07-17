 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults

from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap


import webhelpers.paginate as paginate

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap, permission="administrator")
class Admin(BaseView):

    @view_config(route_name='admin.index', renderer='altair.app.ticketing:templates/admin/index.html')
    def index(self):
        return dict()

    @view_config(route_name='admin.organization', renderer='altair.app.ticketing:templates/admin/organization.html')
    def organization(self):
        return dict()

    @view_config(route_name='admin.super', renderer='altair.app.ticketing:templates/admin/organization.html')
    def super(self):
        return dict()
