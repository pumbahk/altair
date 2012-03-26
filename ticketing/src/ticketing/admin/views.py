# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from ticketing.views import BaseView

from ticketing.fanstatic import with_bootstrap

@view_defaults(decorator=with_bootstrap,  permission='admin')
class Admin(BaseView):

    @view_config(route_name='admin.index', renderer='ticketing:templates/admin/index.html')
    def index(self):
        return {}