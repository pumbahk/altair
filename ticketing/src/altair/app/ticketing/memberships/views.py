# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import webhelpers.paginate as paginate
from altair.app.ticketing.models import merge_session_with_post
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as cmodels
from altair.app.ticketing.users import models as umodels
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from . import forms
from altair.app.ticketing.response import refresh_response
from pyramid.response import Response
## admin権限を持っている人以外見れない想定。

@view_defaults(permission="member_editor", decorator=with_bootstrap, route_name="memberships")
class MembershipView(BaseView):
    @view_config(match_param="action=index", renderer="altair.app.ticketing:templates/memberships/index.html")
    def index(self):
        organization_id = self.context.user.organization_id
        memberships = umodels.Membership.query.filter_by(organization_id=organization_id)
        return {"memberships": memberships}

    @view_config(match_param="action=show", renderer="altair.app.ticketing:templates/memberships/show.html")
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
                "form_mg_delete": forms.MemberGroupDeleteForm(membership_id=membership.id, redirect_to=self.request.url),
                "membergroups": membergroups,
                "redirect_to": redirect_to}

    @view_config(match_param="action=new", renderer="altair.app.ticketing:templates/memberships/new.html", request_method="GET")
    def new_get(self):
        organization_id = self.context.user.organization_id
        return {"form":forms.MembershipForm(organization_id=organization_id)}

    @view_config(match_param="action=new", renderer="altair.app.ticketing:templates/memberships/new.html", request_method="POST")
    def new_post(self):
        form = forms.MembershipForm(self.request.POST)
        if not form.validate():
            return {"form":form}
        membership = umodels.Membership(name=form.data["name"],
                                        display_name=form.data["display_name"],
                                        organization_id=form.data["organization_id"],
                                        enable_auto_input_form=form.data['enable_auto_input_form'],
                                        enable_point_input=form.data['enable_point_input'],
                                        memo=form.data['memo'])
        DBSession.add(membership)
        self.request.session.flash(u"membershipを保存しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))

    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/edit.html", request_method="GET")
    def edit_get(self):
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"], 
                                                        organization_id = self.context.user.organization_id).first()
        if membership is None:
            raise HTTPNotFound

        form = forms.MembershipForm(obj=membership)
        return {"membership": membership, "form":form}

    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/edit.html", request_method="POST")
    def edit_post(self):
        form = forms.MembershipForm(self.request.POST)
        if not form.validate():
            return {"form":form}

        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        membership.name=form.data["name"]
        membership.display_name=form.data['display_name']
        membership.organization_id=form.data["organization_id"]
        membership.memo=form.data['memo']
        membership.enable_auto_input_form=form.data["enable_auto_input_form"]
        membership.enable_point_input=form.data["enable_point_input"]

        DBSession.add(membership)
        self.request.session.flash(u"membershipを編集しました")
        return HTTPFound(self.request.route_url("memberships", action="index", membership_id="*"))

    @view_config(match_param="action=delete")
    def delete(self):
        membership = umodels.Membership.query.filter_by(id=self.request.matchdict["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound
        if len(membership.membergroups) > 0:
            return Response(u"""
            <div class="alert alert-error">
            {membership.name}には１つ以上の会員区分が存在しています。消せません。
            </div>
            """.format(membership=membership))
        membership.delete()
        self.request.session.flash(u"membershipを削除しました")
        return refresh_response(self.request, {"redirect_to": self.request.route_url("memberships", action="index", membership_id="*")})


@view_defaults(decorator=with_bootstrap, route_name="membergroups", permission="member_editor")
class MemberGroupView(BaseView):
    @view_config(match_param="action=show", renderer="altair.app.ticketing:templates/memberships/groups/show.html")
    def show(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        if membergroup is None:
            raise HTTPNotFound
        sales_segment_groups = membergroup.sales_segment_groups
        redirect_to = self.request.url
        return {"membergroup": membergroup, 
                "form": forms.MemberGroupForm(),
                "delete_form": forms.MemberGroupDeleteForm(obj=membergroup, redirect_to=""), 
                "redirect_to": redirect_to, 
                "sales_segment_groups": sales_segment_groups}

    @view_config(match_param="action=new", renderer="altair.app.ticketing:templates/memberships/groups/new.html", 
                 request_param="membership_id", request_method="GET")
    def new_get(self):
        membership = umodels.Membership.query.filter_by(id=self.request.params["membership_id"]).first()
        if membership is None:
            raise HTTPNotFound
        form = forms.MemberGroupForm(membership_id=membership.id)
        return {"form": form, "redirect_to": self.request.params["redirect_to"]}

    @view_config(match_param="action=new", renderer="altair.app.ticketing:templates/memberships/groups/new.html", 
                 request_param="membership_id", request_method="POST")
    def new_post(self):
        form = forms.MemberGroupForm(self.request.POST)
        if not form.validate():
            return {"form": form, "redirect_to":self.request.params["redirect_to"]}

        membergroup = umodels.MemberGroup(name=form.data["name"], 
                                          membership_id=form.data["membership_id"], 
                                          is_guest=form.data["is_guest"],
                                          )
        DBSession.add(membergroup)
        self.request.session.flash(u"membergroupを保存しました")
        dummy_url = self.request.route_path("memberships", action="index", membership_id="*") ## this is dummy
        return HTTPFound(self.request.POST.get("redirect_to") or dummy_url)

    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/groups/edit.html", 
                 request_param="membership_id", request_method="GET")
    def edit_get(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"], 
                                                          membership_id=self.request.params["membership_id"]).first()
        if membergroup is None:
            raise HTTPNotFound
        form = forms.MemberGroupForm(obj=membergroup)
        return {"form": form, "redirect_to": self.request.params["redirect_to"], "membergroup": membergroup}

    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/groups/edit.html", 
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

    @view_config(match_param="action=delete", request_method="POST", renderer="altair.app.ticketing:templates/common/simpleform.html")
    def delete_post(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        if membergroup is None:
            raise HTTPNotFound("member group not found")
        form = forms.MemberGroupDeleteForm(self.request.POST, obj=membergroup)
        if not form.validate():
            return {"form": form}
        membership_id=membergroup.membership_id
        membergroup.delete()
        self.request.session.flash(u"membergroupを削除しました")
        dummy_url = self.request.route_path("memberships", action="show", membership_id=membership_id) ## this is dummy
        return refresh_response(self.request, {"redirect_to": self.request.POST.get("redirect_to") or dummy_url})

@view_config(route_name="membergrups.api.sales_segment_groups.candidates", permission="member_editor",
             request_method="GET", xhr=True, renderer="json")
def candidates_sales_segment_group(context, request):
    qs = cmodels.SalesSegmentGroup.query
    event_id = request.matchdict["event_id"]
    if event_id != "*":
        qs = qs.filter(cmodels.Event.id==event_id, cmodels.SalesSegmentGroup.event_id==cmodels.Event.id)
    sales_segment_groups = [{"id": s.id, "name": s.name} for s in qs]
    return {"status": "success", "sales_segment_groups": sales_segment_groups}

@view_defaults(decorator=with_bootstrap, route_name="membergroups.sales_segment_groups", permission="member_editor")
class SalesSegmentView(BaseView):
    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/salessegments/edit.html", 
                 request_method="GET")
    def edit_get(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        candidates_sales_segment_groups = []
        events = cmodels.Event.query.filter_by(organization_id=self.context.user.organization_id)

        ## optinal
        event_id=self.request.params.get("event_id")
        if event_id:
            events.filter_by(id=event_id)

        form = forms.SalesSegmentGroupToMemberGroupForm(obj=membergroup, 
                                                   sales_segment_groups=candidates_sales_segment_groups,
                                                   events=events)
        return {"form": form, 
                "redirect_to": self.request.params["redirect_to"], 
                "membergroup_id": self.request.params["membergroup_id"], 
                "sales_segment_groups_source": self.request.route_path("membergrups.api.sales_segment_groups.candidates", event_id="__id__"), 
                "membergroup": membergroup, 
                "form_mg": forms.MemberGroupForm()}


    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/memberships/salessegments/edit.html", 
                 request_method="POST")
    def edit_post(self):
        membergroup = umodels.MemberGroup.query.filter_by(id=self.request.matchdict["membergroup_id"]).first()
        event_id = unicode(self.request.POST["event_id"])
        candidates_sales_segment_groups = cmodels.SalesSegmentGroup.query
        will_bounds = candidates_sales_segment_groups.filter(cmodels.SalesSegmentGroup.id.in_(self.request.POST.getall("sales_segment_groups")))

        will_removes = {}
        for s in membergroup.sales_segment_groups:
            if unicode(s.event_id) == event_id:
                will_removes[unicode(s.id)] = s

        for s in will_bounds:
            if unicode(s.id) in will_removes:
                del will_removes[unicode(s.id)]
            else:
                membergroup.sales_segment_groups.append(s)
        for s in will_removes.values():
            membergroup.sales_segment_groups.remove(s)

        DBSession.add(membergroup)
        self.request.session.flash(u'販売区分グループの結びつき変更しました')
        return HTTPFound(self.request.POST["redirect_to"])
