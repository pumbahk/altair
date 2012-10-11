# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ticketing.models import DBSession
from ticketing.core import models as cmodels
from ticketing.users import models as umodels
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from . import forms
from ticketing.events.sales_segments.forms import MemberGroupForm

@view_defaults(permission="administrator", decorator=with_bootstrap, route_name="memberships")
class MembershipView(BaseView):
    @view_config(match_param="action=index", renderer="ticketing:templates/memberships/index.html")
    def index(self):
        memberships = umodels.Membership.query
        return {"memberships": memberships}

    @view_config(match_param="action=show", renderer="ticketing:templates/memberships/show.html")
    def show(self):
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound
        membergroups = membership.membergroups
        return {"membership": membership,
                "form": forms.MembershipForm(),
                "form_mg": MemberGroupForm(), 
                "membergroups": membergroups}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/new.html", request_method="GET")
    def new_get(self):
        return {"form":forms.MembershipForm()}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/new.html", request_method="POST")
    def new_post(self):
        form = forms.MembershipForm(self.request.POST)
        if not form.validate():
            return {"form":form}
        membership = umodels.Membership(name=form.data["name"], 
                           organization_id=form.data["organization_id"])
        DBSession.add(membership)
        self.request.session.flash(u"membershipを保存しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/edit.html", request_method="GET")
    def edit_get(self):
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound

        form = forms.MembershipForm(obj=membership)
        return {"membership": membership, "form":form}

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/edit.html", request_method="POST")
    def edit_post(self):
        form = forms.MembershipForm(self.request.POST)
        if not form.validate():
            return {"form":form}

        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        membership.name=form.data["name"]
        membership.organization_id=form.data["organization_id"]

        DBSession.add(membership)
        self.request.session.flash(u"membershipを編集しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))

    @view_config(match_param="action=delete", renderer="ticketing:templates/memberships/delete.html")
    def delete(self):
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound
        DBSession.delete(membership)
        self.request.session.flash(u"membershipを削除しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))
