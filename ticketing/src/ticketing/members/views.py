# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
import json
import webhelpers.paginate as paginate
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, view_defaults
from ticketing.fanstatic import with_bootstrap
from ticketing.users.models import Membership, MemberGroup, Member, User, UserCredential
from . import forms
from . import api

def correct_organization(info, request):
    return unicode(info.user.organization_id) == request.matchdict.get("organization_id")


@view_config(route_name="members.empty", 
             decorator=with_bootstrap, renderer="ticketing:templates/members/index.html")
def members_empty_view(context, request):
    membership = context.memberships.first()
    url = request.route_url("members.index", membership_id=membership.id)
    return HTTPFound(url)

@view_config(route_name="members.index", 
             decorator=with_bootstrap, renderer="ticketing:templates/members/index.html")
def members_index_view(context, request):
    membership_id = request.matchdict["membership_id"]
    memberships = context.memberships
    choice_form = forms.MemberShipChoicesForm().configure(memberships)

    users = User.query.filter(User.id==UserCredential.user_id)\
        .filter(UserCredential.membership_id==membership_id)\
        .filter(Member.user_id==User.id)\
        .options(orm.joinedload("user_credential"), 
                 orm.joinedload("user_credential.membership"), 
                 orm.joinedload("member"), 
                 orm.joinedload("member.membergroup"), 
                 )

    users = paginate.Page(
        users, 
        item_count=users.count(), 
        page=int(request.params.get('page', 0)),
        items_per_page=50,
        url=paginate.PageURL_WebOb(request)
        )
    return {"users": users, "choice_form": choice_form, 
            "membership_id": membership_id}

@view_defaults(route_name="members.member", decorator=with_bootstrap)
class MemberView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="action=edit_dialog", 
                 renderer="ticketing:templates/members/_edit_member_dialog.html")
    def edit_member_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        membergroups = self.context.membergroups  
        form = forms.MemberGroupChoicesForm(user_id_list=self.request.params["user_id_list"])
        form = form.configure(membergroups)

        users = User.query.filter(User.id.in_(json.loads(form.data["user_id_list"])))\
            .options(orm.joinedload("user_credential"), 
                     orm.joinedload("member"), 
                     orm.joinedload("member.membergroup"), 
                     orm.joinedload("member.membergroup.membership"), 
                     )
        return {"users": users, "form": form, "membership_id": membership_id}

    @view_config(match_param="action=edit", 
                 renderer="json")
    def edit_member(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberGroupChoicesForm(self.request.POST)

        if not form.validate():
            self.request.session.flash(unicode(form.errors))
            return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

        api.edit_membergroup(Member.query.filter(Member.user_id.in_(form.data["user_id_list"])), 
                             form.data["membergroup_id"])

        self.request.session.flash(u"membergroupを変更しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

    @view_config(match_param="action=csv_import_dialog", 
                 renderer="ticketing:templates/members/_csv_import_dialog.html")
    def csv_import_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVImportForm()
        return {"form": form, "membership_id": membership_id}

    @view_config(match_param="action=csv_import", 
                 renderer="ticketing:templates/members/_csv_import_dialog.html")
    def csv_import(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVImportForm(self.request.POST)
        if not form.validate():
            return {"form": form, "membership_id": membership_id}
        
        api.members_import_from_csv(self.request, form.data["csvfile"].file)
        self.request.session.flash(u"membergroupを変更しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

