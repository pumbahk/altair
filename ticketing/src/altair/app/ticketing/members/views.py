# -*- coding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
import json
import webhelpers.paginate as paginate
from StringIO import StringIO
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config, view_defaults

from altair.app.ticketing.models import merge_session_with_post
from altair.response import FileLikeResponse ##
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.users.models import Member, User, MemberGroup, Membership
from . import forms
from . import api
from altair.app.ticketing.views import BaseView

def correct_organization(info, request):
    """ [separation] super userか自身の所属するOrganizationのもののみ表示
    """
    if info.user is None:
        return False
    if info.user.is_superuser:
        return True
    if "membership_id" in request.matchdict:
        return info.memberships.filter_by(id = request.matchdict["membership_id"]).first()
    return False

@view_config(route_name="members.membership.index", 
             permission="member_editor",
             decorator=with_bootstrap, renderer="altair.app.ticketing:templates/members/membership_index.html")
def members_membership_index_view(context, request):
    memberships = context.memberships
    return {"memberships": memberships}

@view_config(route_name="members.index", 
             permission="member_editor",
             custom_predicates=(correct_organization, ), 
             decorator=with_bootstrap, renderer="altair.app.ticketing:templates/members/index.html")
def members_index_view(context, request):
    membership_id = request.matchdict["membership_id"]
    memberships = context.memberships
    membership = memberships.filter_by(id=membership_id).first()
    if membership is None:
        return HTTPNotFound(u"membershipが登録されていません。")
    membergroup_id = request.GET.get("membergroup_id")
    username = request.GET.get("username")

    choice_form = forms.SearchMemberForm(membership_id=membership_id, membergroup_id=membergroup_id, username=username)\
        .configure(memberships, membership.membergroups)

    users = User.query.join(User.member) \
        .filter(Member.membership_id==membership_id)\
        .filter(Member.user_id==User.id)\
        .options(orm.contains_eager(User.member), 
                 orm.joinedload(User.member, Member.membergroup), 
                 )

    if membergroup_id:
        users = users.filter(Member.membergroup_id == membergroup_id)
    if username:
        users = users.filter(Member.auth_identifier.like(u"%%%s%%" % username))

    users = paginate.Page(
        users, 
        item_count=users.count(), 
        page=int(request.params.get('page', 0)),
        items_per_page=50,
        url=paginate.PageURL_WebOb(request)
        )
    membergroups = MemberGroup.query.filter_by(membership_id=membership.id).order_by(sa.asc(MemberGroup.name)).all()
    return {"users": users,
            "choice_form": choice_form, 
            "membership": membership, 
            "membergroup_id": membergroup_id, 
            "membergroups": membergroups}

@view_defaults(route_name="members.member", permission="member_editor", decorator=with_bootstrap)
class MemberView(BaseView):
    @view_config(match_param="action=delete_all_dialog", 
                 renderer="altair.app.ticketing:templates/members/_delete_member_all_dialog.html")
    def delete_member_all_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        membergroup_id = self.request.GET.get("membergroup_id", "")
        membership = Membership.query.filter_by(id=membership_id).first()
        if membership is None:
            raise HTTPFound("not found")
        if membergroup_id:
            membergroup = MemberGroup.query.filter_by(membership_id=membership_id, id=membergroup_id).first()
        else:
            membergroup = None
        return {"membership": membership, 
                "membergroup": membergroup, 
                }

    @view_config(match_param="action=delete_all", 
                 renderer="json")
    def delete_member_all(self):
        membergroup_id = self.request.POST["membergroup_id"]
        membership_id = self.request.matchdict["membership_id"]
        users = User.query.join(User.member) \
                          .filter(Member.membership_id == membership_id)
        if membergroup_id:
            users = users.filter(Member.membergroup_id==membergroup_id,)
        api.delete_loginuser(self.request, users)
        self.request.session.flash(u"ユーザを一括削除しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

    @view_config(match_param="action=delete_dialog", 
                 renderer="altair.app.ticketing:templates/members/_delete_member_dialog.html")
    def delete_member_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        user_id_list = self.request.params["user_id_list"]
        users = User.query.filter(User.id.in_(json.loads(user_id_list)))\
            .join(User.member)\
            .options(orm.contains_eager(User.member), 
                     orm.joinedload(User.member, Member.membergroup), 
                     orm.joinedload(User.member, Member.membership)
                     )
        return {"users": users,"membership_id": membership_id, "user_id_list": user_id_list}


    @view_config(match_param="action=delete", 
                 renderer="json")
    def delete_member(self):
        user_id_list = self.request.params["user_id_list"]
        membership_id = self.request.matchdict["membership_id"]
        users = User.query \
            .join(User.member)\
            .filter(User.id.in_(json.loads(user_id_list)))\
            .options(orm.contains_eager(User.member), 
                     orm.joinedload(User.member, Member.membergroup), 
                     orm.joinedload(User.member, Member.membership),
                     )
        api.delete_loginuser(self.request, users)
        self.request.session.flash(u"指定したユーザを削除しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

    @view_config(match_param="action=edit_dialog", 
                 renderer="altair.app.ticketing:templates/members/_edit_member_dialog.html")
    def edit_member_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        membergroups = self.context.membergroups  
        form = forms.MemberGroupChoicesForm(user_id_list=self.request.params["user_id_list"])
        form = form.configure(membergroups)

        users = User.query \
            .join(User.member)\
            .filter(User.id.in_(json.loads(form.data["user_id_list"])))\
            .options(orm.contains_eager(User.member), 
                     orm.joinedload(User.member, Member.membergroup), 
                     orm.joinedload(User.member, Member.membership)
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

        api.edit_membergroup(self.request, Member.query.filter(Member.user_id.in_(form.data["user_id_list"])), 
                             form.data["membergroup_id"])

        self.request.session.flash(u"membergroupを変更しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

    @view_config(match_param="action=csv_import_dialog", 
                 renderer="altair.app.ticketing:templates/members/_csv_import_dialog.html")
    def csv_import_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVImportForm()
        return {"form": form, "membership_id": membership_id}

    @view_config(match_param="action=csv_import", 
                 renderer="altair.app.ticketing:templates/members/csv_import_confirm.html")
    def csv_import(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVImportForm(self.request.POST)
        if not form.validate():
            return {"form": form, "membership_id": membership_id}
        
        api.members_import_from_csv(self.request, form.data["csvfile"].file, encoding=form.data["encoding"])
        self.request.session.flash(u"membergroupを変更しました")
        return HTTPFound(self.request.route_url("members.index", membership_id=membership_id))

    @view_config(match_param="action=csv_export_dialog", 
                 renderer="altair.app.ticketing:templates/members/_csv_export_dialog.html")
    def csv_export_dialog(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVExportForm(csvfile=u"membership.csv")
        return {"form": form, "membership_id": membership_id}

    @view_config(match_param="action=csv_export", 
                 renderer="altair.app.ticketing:templates/members/_csv_export_dialog.html")
    def csv_export(self):
        membership_id = self.request.matchdict["membership_id"]
        form = forms.MemberCSVExportForm(self.request.POST)
        if not form.validate():
            return {"form": form, "membership_id": membership_id}

        io = StringIO()
        users = User.query \
            .join(User.member)\
            .filter(Member.membership_id==membership_id)\
            .options(orm.contains_eager(User.member),
                     orm.joinedload(User.member, Member.membergroup), 
                     orm.joinedload(User.member, Member.membership)
                     )
        api.members_export_as_csv(self.request, io, users, encoding=form.data["encoding"])

        if "cp932" == form.data["encoding"]:
            content_encoding = "shift-JIS"
        else:
            content_encoding = form.data["encoding"]
        return FileLikeResponse(io, request=self.request, 
                                filename=form.data["csvfile"].encode("utf-8"),
                                content_encoding=content_encoding)


@view_defaults(permission="member_editor", decorator=with_bootstrap, route_name="members.loginuser")
class LoginUserView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(match_param="action=edit", renderer="altair.app.ticketing:templates/members/_edit_loginuser_dialog.html", request_method="GET")
    def edit_dialog(self):
        loginuser = Member.filter_by(id=self.request.matchdict["loginuser_id"]).first()
        form = forms.LoginUserEditForm(auth_identifier=loginuser.auth_identifier, 
                                       auth_secret=loginuser.auth_secret,
                                       )
        return {"form": form}

    @view_config(match_param="action=edit", request_method="POST")
    def edit(self):
        membership_id = self.request.matchdict["membership_id"]
        qs = Member.filter(Member.membership_id==membership_id)
        loginuser = qs.filter_by(id=self.request.matchdict["loginuser_id"]).first()
        form = forms.LoginUserEditForm(self.request.POST)

        if form.object_validate(qs, loginuser):
            loginuser = merge_session_with_post(loginuser, form.data)
            loginuser.save()
            self.request.session.flash(u"loginuserの設定を変更しました")
            return HTTPFound(self.request.route_path("members.index", membership_id=membership_id))
        else:
            self.request.session.flash(u"同じ名前(%s)が既に登録されています" % form.data["auth_identifier"])
            return HTTPFound(self.request.route_path("members.index", membership_id=membership_id))

