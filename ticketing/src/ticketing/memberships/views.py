# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import webhelpers.paginate as paginate
from ticketing.models import merge_session_with_post
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from ticketing.models import DBSession
from ticketing.core import models as cmodels
from ticketing.users import models as umodels
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from . import forms
from ticketing.events.sales_segments.forms import SalesSegmentForm

## admin権限を持っている人以外見れない想定。

@view_defaults(permission="administrator", decorator=with_bootstrap, route_name="memberships")
class MembershipView(BaseView):
    @view_config(match_param="action=index", renderer="ticketing:templates/memberships/index.html")
    def index(self):
        organization_id = self.context.user.organization_id
        memberships = umodels.Membership.query.filter_by(organization_id=organization_id)
        return {"memberships": memberships}

    @view_config(match_param="action=show", renderer="ticketing:templates/memberships/show.html")
    def show(self):
        organization_id = self.context.user.organization_id
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"], 
                                                        organization_id=organization_id).first()
        if membership is None:
            raise HTTPNotFound
        membergroups = membership.membergroups
        redirect_to = self.request.url
        return {"membership": membership,
                "form": forms.MembershipForm(organization_id=organization_id),
                "form_mg": forms.MemberGroupForm(), 
                "membergroups": membergroups, 
                "redirect_to": redirect_to}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/new.html", request_method="GET")
    def new_get(self):
        organization_id = self.context.user.organization_id
        return {"form":forms.MembershipForm(organization_id=organization_id)}

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
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"], 
                                                        organization_id = self.context.user.organization_id).first()
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
        membership.delete()
        self.request.session.flash(u"membershipを削除しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))

@view_defaults(decorator=with_bootstrap, route_name="membergroups", permission="administrator")
class MemberGroupView(BaseView):
    @view_config(match_param="action=show", renderer="ticketing:templates/memberships/groups/show.html")
    def show(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        if membergroup is None:
            raise HTTPNotFound
        salessegments = membergroup.sales_segments
        redirect_to = self.request.url
        return {"membergroup": membergroup, 
                "form": forms.MemberGroupForm(), 
                "redirect_to": redirect_to, 
                "salessegments": salessegments, 
                "form_sg": SalesSegmentForm()}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/groups/new.html", 
                 request_param="membership_id", request_method="GET")
    def new_get(self):
        membership = umodels.Membership.query.filter_by(id=self.request.params["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound
        form = forms.MemberGroupForm(membership_id=membership.id)
        return {"form": form, "redirect_to": self.request.params["redirect_to"]}

    @view_config(match_param="action=new", renderer="ticketing:templates/memberships/groups/new.html", 
                 request_param="membership_id", request_method="POST")
    def new_post(self):
        form = forms.MemberGroupForm(self.request.POST)
        if not form.validate():
            return {"form": form, "redirect_to":self.request.params["redirect_to"]}

        membergroup = umodels.MemberGroup(name=form.data["name"], 
                                          membership_id=form.data["membership_id"], 
                                          is_guest=form.data["is_guest"])
        DBSession.add(membergroup)
        self.request.session.flash(u"membergroupを保存しました")
        dummy_url = self.request.route_path("memberships", action="index", membership_id="*") ## this is dummy
        return HTTPFound(self.request.POST.get("redirect_to") or dummy_url)

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/groups/edit.html", 
                 request_param="membership_id", request_method="GET")
    def edit_get(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"], 
                                                          membership_id=self.request.params["membership_id"]).first()
        if membergroup is None:
            raise HTTPNotFound
        form = forms.MemberGroupForm(obj=membergroup)
        return {"form": form, "redirect_to": self.request.params["redirect_to"], "membergroup": membergroup}

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/groups/edit.html", 
                 request_param="membership_id", request_method="POST")
    def edit_post(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"], 
                                                          membership_id=self.request.params["membership_id"]).first()
        if membergroup is None:
            raise HTTPNotFound

        form = forms.MemberGroupForm(self.request.POST)
        if not form.validate():
            return {"form": form, "redirect_to": self.request.params["redirect_to"], "membergroup": membergroup}

        membergroup.name=form.data["name"]
        membergroup.membership_id=form.data["membership_id"]
        membergroup.is_guest=form.data["is_guest"]
        DBSession.add(membergroup)

        self.request.session.flash(u"membergroupを更新しました")
        dummy_url = self.request.route_path("memberships", action="index", membership_id="*") ## this is dummy
        return HTTPFound(self.request.POST.get("redirect_to") or dummy_url)

    @view_config(match_param="action=delete", 
                 request_method="POST")
    def delete_post(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        if membergroup is None:
            raise HTTPNotFound("member group not found")

        membergroup.delete()

        self.request.session.flash(u"membergroupを削除しました")
        dummy_url = self.request.route_path("memberships", action="index", membership_id="*") ## this is dummy
        return HTTPFound(self.request.POST.get("redirect_to") or dummy_url)

@view_config(route_name="membergrups.api.salessegments.candidates", permission="administrator", 
             request_method="GET", xhr=True, renderer="json")
def candidates_sales_segment(context, request):
    qs = cmodels.SalesSegment.query
    event_id = request.matchdict["event_id"]
    if event_id != "*":
        qs = qs.filter(cmodels.Event.id==event_id, cmodels.SalesSegment.event_id==cmodels.Event.id)
    salessegments = [{"id": s.id, "name": s.name} for s in qs]
    return {"status": "success", "salessegments": salessegments}

@view_defaults(decorator=with_bootstrap, route_name="membergroups.salessegments", permission="administrator")
class SalesSegmentView(BaseView):
    # @view_config(match_param="action=new", renderer="ticketing:templates/memberships/salessegments/new.html", 
    #              request_param="membergroup_id", request_method="GET")
    # def new_get(self):
    #     form = SalesSegmentForm()
    #     return {"form": form, 
    #             "redirect_to": self.request.params["redirect_to"], 
    #             "membergroup_id": self.request.params["membergroup_id"], 
    #             }

    # @view_config(match_param="action=new", renderer="ticketing:templates/memberships/salessegments/new.html", 
    #              request_param="membergroup_id", request_method="POST")
    # def new_post(self):
    #     form = SalesSegmentForm(self.request.POST)
    #     if not form.validate():
    #         return {"form": form, 
    #                 "redirect_to": self.request.params["redirect_to"], 
    #                 "membergroup_id": self.request.params["membergroup_id"], 
    #                 }

    #     membergroup = umodels.MemberGroup.query.filter_by(id=self.request.params["membergroup_id"]).first()
    #     sales_segment = merge_session_with_post(cmodels.SalesSegment(), form.data)
    #     membergroup.sales_segments.append(sales_segment)

    #     DBSession.add(membergroup)        
    #     DBSession.add(sales_segment)

    #     self.request.session.flash(u'販売区分を保存しました')
    #     return HTTPFound(self.request.POST["redirect_to"])

    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/salessegments/edit.html", 
                 request_method="GET")
    def edit_get(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        candidates_salessegments = []
        events = cmodels.Event.query.filter_by(organization_id=self.context.user.organization_id)

        ## optinal
        event_id=self.request.params.get("event_id")
        if event_id:
            events.filter_by(id=event_id)

        form = forms.SalesSegmentToMemberGroupForm(obj=membergroup, 
                                                   salessegments=candidates_salessegments,
                                                   events=events)
        return {"form": form, 
                "redirect_to": self.request.params["redirect_to"], 
                "membergroup_id": self.request.params["membergroup_id"], 
                "salessegments_source": self.request.route_path("membergrups.api.salessegments.candidates", event_id="__id__"), 
                "membergroup": membergroup, 
                "form_mg": forms.MemberGroupForm(), 
                "form_sg": SalesSegmentForm()}


    @view_config(match_param="action=edit", renderer="ticketing:templates/memberships/salessegments/edit.html", 
                 request_method="POST")
    def edit_post(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        event_id = unicode(self.request.POST["event_id"])
        candidates_salessegments = cmodels.SalesSegment.query
        will_bounds = candidates_salessegments.filter(cmodels.SalesSegment.id.in_(self.request.POST.getall("salessegments")))

        will_removes = {}
        for s in membergroup.sales_segments:
            if unicode(s.event_id) == event_id:
                will_removes[unicode(s.id)] = s

        for s in will_bounds:
            if unicode(s.id) in will_removes:
                del will_removes[unicode(s.id)]
            else:
                membergroup.sales_segments.append(s)
        for s in will_removes.values():
            membergroup.sales_segments.remove(s)

        DBSession.add(membergroup)
        self.request.session.flash(u'販売区分の結びつき変更しました')
        return HTTPFound(self.request.POST["redirect_to"])
