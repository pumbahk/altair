# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ticketing.core import models as cmodels
from ticketing.users import models as umodels
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

@view_defaults(permission="administrator", decorator=with_bootstrap, route_name="memberships")
class MembershipView(BaseView):
    @view_config(match_param="action=index", renderer="ticketing:templates/memberships/index.html")
    def index(self):
        memberships = umodels.Membership.query
        return {"memberships": memberships}

    @view_config(match_param="action=show", renderer="ticketing:templates/memberships/show.html")
    def show(self):
        return {}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/new.html")
    def new(self):
        return {}

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/edit.html")
    def edit(self):
        return {}

    @view_config(match_param="action=delete", renderer="ticketing:templates/memberships/delete.html")
    def delete(self):
        return {}



