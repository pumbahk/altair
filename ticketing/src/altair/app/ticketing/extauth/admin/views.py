# encoding: utf-8

import logging
import functools
import json
import datetime
from datetime import timedelta
from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPBadRequest
from pyramid.security import remember, forget
from pyramid_layout.panel import panel_config
from webhelpers import paginate
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import class_mapper
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.sqlahelper import get_db_session
from .api import create_operator, lookup_operator_by_credentials, lookup_organization_by_name, lookup_organization_by_id
from ..models import MemberSet, MemberKind, Member, Membership, OAuthClient
from ..api import create_member
from ..utils import digest_secret, generate_salt, generate_random_alnum_string
from .forms import (
    LoginForm,
    OrganizationForm,
    OperatorForm,
    MemberSetForm,
    MemberKindForm,
    MemberForm,
    OAuthClientForm,
    HostForm,
    OAuthServiceProviderForm
)
from .models import Operator
from ..models import Organization, Host, OAuthServiceProvider
from . import import_export

logger = logging.getLogger(__name__)

def get_object_queryset(request, klass, db_session=None):
    if not db_session:
        db_session=get_db_session(request, 'extauth_slave')
    query = db_session.query(klass)
    if not request.operator.is_administrator:
        if klass == Organization:
            query = query.filter_by(id=request.operator.organization_id)
        else:
            query = query.filter_by(organization_id=request.operator.organization_id)
    return query

@forbidden_view_config()
def forbbidden(context, request):
    if not request.authenticated_userid:
        return HTTPFound(request.route_path('login', _query=dict(return_url=request.path)))
    else:
        return context

@view_defaults(
    route_name='login',
    renderer='login.mako',
    decorator=(with_bootstrap,)
    )
class LoginView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='login', renderer='login.mako')
    def get(self):
        return_url = self.request.params.get('return_url', '')
        return dict(form=LoginForm(), return_url=return_url)
        
    @view_config(route_name='login', request_method='POST', renderer='login.mako')
    def post(self):
        return_url = self.request.params.get('return_url')
        if not return_url:
            return_url = self.request.route_path('top')
        form = LoginForm(formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, return_url=return_url)
        operator = lookup_operator_by_credentials(
            self.request,
            form.user_name.data,
            form.password.data
            )
        if operator is None:
            self.request.session.flash(u'ユーザ名とパスワードの組み合わせが誤っています')
            return dict(form=form, return_url=return_url)

        remember(self.request, operator.id)
        return HTTPFound(return_url)


@view_config(
    route_name='logout',
    permission='authenticated'
    )
def logout(context, request):
    forget(request)
    return HTTPFound(request.route_path('top'))


@view_config(
    route_name='top',
    renderer='top.mako',
    permission='authenticated',
    decorator=(with_bootstrap,)
    )
def top(context, request):
    return dict()


@view_defaults(
    decorator=(with_bootstrap,)
    )
class OrganizationsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='organizations.index',
        renderer='organizations/index.mako',
        permission='manage_organization',
        request_method='GET'
        )
    def index(self):
        organizations = get_object_queryset(request=self.request, klass=Organization)
        if self.request.operator.is_administrator or self.request.operator.is_superoperator:
            organizations = organizations.all()
        else:
            raise HTTPForbidden()
        return dict(
            organizations=organizations
            )

    @view_config(
        route_name='organizations.new',
        renderer='organizations/edit.mako',
        permission='administration',
        request_method='GET'
        )
    def new(self):
        form = OrganizationForm(request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='organizations.new',
        renderer='organizations/edit.mako',
        permission='administration',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = OrganizationForm(formdata=self.request.POST, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        organization = Organization(
            maximum_oauth_scope=form.maximum_oauth_scope.data,
            canonical_host_name=form.canonical_host_name.data,
            emergency_exit_url=form.emergency_exit_url.data,
            settings=form.settings.data,
            short_name=form.short_name.data,
            fanclub_api_type=form.fanclub_api_type.data,
            fanclub_api_available=form.fanclub_api_available.data,
            invalidate_client_http_session_on_access_token_revocation=form.invalidate_client_http_session_on_access_token_revocation.data
        )
        session.add(organization)
        session.flush()
        session.commit()
        self.request.session.flash(u'Organization %s を新規作成しました' % organization.short_name)
        return HTTPFound(location=self.request.route_path('organizations.edit', id=organization.id))

    @view_config(
        route_name='organizations.edit',
        renderer='organizations/edit.mako',
        permission='manage_organization',
        request_method='GET'
        )
    def edit(self):
        form = OrganizationForm(obj=self.context.organization, request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='organizations.edit',
        renderer='organizations/edit.mako',
        permission='manage_organization',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        organization = self.context.organization
        form = OrganizationForm(formdata=self.request.POST, obj=organization, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        form.populate_obj(organization)
        session.commit()
        self.request.session.flash(u'Organization %s を変更しました' % organization.short_name)
        return HTTPFound(location=self.request.route_path('organizations.edit', id=organization.id))


@view_defaults(
    decorator=(with_bootstrap,)
    )
class HostsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='hosts.new',
        renderer='hosts/edit.mako',
        permission='manage_organization',
        request_method='GET'
        )
    def new(self):
        form = HostForm(request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='hosts.new',
        renderer='hosts/edit.mako',
        permission='manage_organization',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        host = Host()
        form = HostForm(formdata=self.request.POST, obj=host, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        host.host_name = form.host_name.data
        host.organization_id = self.request.matchdict['id']
        session.add(host)
        session.commit()
        self.request.session.flash(u'Host %s を新規作成しました' % host.host_name)
        return HTTPFound(location=self.request.route_path('organizations.edit', id=self.request.matchdict['id']))


@view_defaults(
    permission='manage_operators',
    decorator=(with_bootstrap,)
    )
class OperatorsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='operators.index',
        renderer='operators/index.mako',
        permission='manage_operators'
        )
    def index(self):
        query = get_object_queryset(request=self.request, klass=Operator)
        if self.request.operator.is_administrator:
            query = query.all()
        elif self.request.operator.is_superoperator:
            query = query.filter(Operator.role_id != 1).all()
        else:
            raise HTTPForbidden()

        operators = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
            )
        return dict(
            operators=operators
            )

    @view_config(
        route_name='operators.edit',
        renderer='operators/edit.mako',
        request_method='GET',
        permission='manage_operators'
        )
    def edit(self):
        operator = self.context.db_session.query(Operator).filter_by(id=self.request.matchdict['id']).one()
        form = OperatorForm(obj=operator, auth_secret=u'', organization_id=str(operator.organization_id),request=self.request)
        return dict(
            form=form,
            operator=operator
            )

    @view_config(
        route_name='operators.edit',
        renderer='operators/edit.mako',
        request_method='POST',
        permission='manage_operators'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        operator = session.query(Operator).filter_by(id=self.request.matchdict['id']).one()
        form = OperatorForm(formdata=self.request.POST, obj=operator, request=self.request)
        if not form.validate():
            return dict(
                form=form,
                operator=operator
                )
        operator.role_id = int(form.role_id.data)
        operator.auth_identifier = form.auth_identifier.data
        if form.auth_secret.data:
            operator.auth_secret = digest_secret(form.auth_secret.data, generate_salt())
        session.add(operator)
        session.commit()
        self.request.session.flash(u'Operator %s を変更しました' % operator.auth_identifier)
        return HTTPFound(location=self.request.route_path('operators.edit', id=operator.id))

    @view_config(
        route_name='operators.new',
        renderer='operators/new.mako',
        request_method='GET',
        permission='manage_operators'
        )
    def new(self):
        form = OperatorForm(organization_id=str(self.request.operator.organization_id), request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='operators.new',
        renderer='operators/new.mako',
        request_method='POST',
        permission='manage_operators'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = OperatorForm(formdata=self.request.POST, new_form=True, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        operator = Operator(
            organization_id = form.organization_id.data,
            auth_identifier=form.auth_identifier.data,
            auth_secret=digest_secret(form.auth_secret.data, generate_salt()),
            role_id=form.role_id.data
        )
        session.add(operator)
        session.commit()
        self.request.session.flash(u'Operator %s を作成しました' % operator.auth_identifier)
        return HTTPFound(location=self.request.route_path('operators.index'))

    @view_config(route_name='operators.delete', permission='manage_operators')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        if self.request.operator.id in id_list:
            self.request.session.flash(u'Operator %s は現在ログイン中のユーザのため削除できません' % self.request.operator.auth_identifier)
            return HTTPFound(location=self.request.route_path('operators.index'))
        query = session.query(Operator).filter_by(organization_id=self.request.operator.organization_id).filter(Operator.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d Operatorを削除しました' % n)
        return HTTPFound(location=self.request.route_path('operators.index'))


@view_defaults(
    permission='manage_member_sets',
    decorator=(with_bootstrap,)
    )
class MemberSetsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='member_sets.index',
        renderer='member_sets/index.mako'
        )
    def index(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id)
        member_sets = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
            )
        return dict(
            member_sets=member_sets
            )

    @view_config(
        route_name='member_sets.edit',
        renderer='member_sets/edit.mako',
        request_method='GET'
        )
    def edit(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id)
        member_set = query.filter_by(id=self.request.matchdict['id']).one()
        form = MemberSetForm(obj=member_set)
        return dict(
            form=form
            )

    @view_config(
        route_name='member_sets.edit',
        renderer='member_sets/edit.mako',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id)
        member_set = query.filter_by(id=self.request.matchdict['id']).one()
        form = MemberSetForm(formdata=self.request.POST)
        if not form.validate():
            return dict(
                form=form
                )
        member_set.name = form.name.data
        member_set.display_name = form.display_name.data
        member_set.applicable_subtype = form.applicable_subtype.data
        member_set.use_password = form.use_password.data
        member_set.auth_identifier_field_name = form.auth_identifier_field_name.data
        member_set.auth_secret_field_name = form.auth_secret_field_name.data
        session.add(member_set)
        session.commit()
        self.request.session.flash(u'会員種別 (MemberSet) %s を変更しました' % member_set.name)
        return HTTPFound(location=self.request.route_path('member_sets.edit', id=member_set.id))

    @view_config(
        route_name='member_sets.new',
        renderer='member_sets/new.mako',
        request_method='GET'
        )
    def new(self):
        form = MemberSetForm()
        return dict(
            form=form
            )

    @view_config(
        route_name='member_sets.new',
        renderer='member_sets/new.mako',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = MemberSetForm(formdata=self.request.POST, new_form=True, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member_set = MemberSet(
            organization=self.request.operator.organization,
            name=form.name.data,
            display_name=form.display_name.data,
            applicable_subtype=form.applicable_subtype.data,
            use_password=form.use_password.data,
            auth_identifier_field_name=form.auth_identifier_field_name.data,
            auth_secret_field_name=form.auth_secret_field_name.data
            )
        session.add(member_set)
        session.commit()
        self.request.session.flash(u'MemberSet %s を作成しました' % member_set.name)
        return HTTPFound(location=self.request.route_path('member_sets.index'))

    @view_config(route_name='member_sets.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        query = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id).filter(MemberSet.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d MemberSet を削除しました' % n)
        return HTTPFound(location=self.request.route_path('member_sets.index'))


@view_defaults(
    permission='manage_member_kinds',
    decorator=(with_bootstrap,)
    )
class MemberKindsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='member_kinds.index',
        renderer='member_kinds/index.mako'
        )
    def index(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberKind).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id)
        member_kinds = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
            )
        return dict(
            member_kinds=member_kinds
            )

    @view_config(
        route_name='member_kinds.edit',
        renderer='member_kinds/edit.mako',
        request_method='GET'
        )
    def edit(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberKind).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id)
        member_kind = query.filter(MemberKind.id == self.request.matchdict['id']).one()
        form = MemberKindForm(obj=member_kind, request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='member_kinds.edit',
        renderer='member_kinds/edit.mako',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(MemberKind).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id)
        member_kind = query.filter(MemberKind.id == self.request.matchdict['id']).one()
        form = MemberKindForm(formdata=self.request.POST, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member_kind.member_set_id = form.member_set_id.data
        member_kind.name = form.name.data
        member_kind.display_name = form.display_name.data
        member_kind.show_in_landing_page = form.show_in_landing_page.data
        member_kind.enable_guests = form.enable_guests.data
        session.add(member_kind)
        session.commit()
        self.request.session.flash(u'会員区分 (MemberKind) %s を変更しました' % member_kind.name)
        return HTTPFound(location=self.request.route_path('member_kinds.edit', id=member_kind.id))

    @view_config(
        route_name='member_kinds.new',
        renderer='member_kinds/new.mako',
        request_method='GET'
        )
    def new(self):
        form = MemberKindForm(request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='member_kinds.new',
        renderer='member_kinds/new.mako',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = MemberKindForm(formdata=self.request.POST, new_form=True, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member_kind = MemberKind(
            member_set_id=form.member_set_id.data,
            name=form.name.data,
            display_name=form.display_name.data,
            show_in_landing_page=form.show_in_landing_page.data,
            enable_guests=form.enable_guests.data
            )
        session.add(member_kind)
        session.commit()
        self.request.session.flash(u'会員区分 (MemberKind) %s を作成しました' % member_kind.name)
        return HTTPFound(location=self.request.route_path('member_kinds.index'))

    @view_config(route_name='member_kinds.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        id_list = [r for r, in session.query(MemberKind.id).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id).filter(MemberKind.id.in_(id_list)) ]
        query = session.query(MemberKind).filter(MemberKind.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d 会員区分 (MemberKind) を削除しました' % n)
        return HTTPFound(location=self.request.route_path('member_kinds.index'))


@view_defaults(
    permission='manage_members',
    decorator=(with_bootstrap,)
    )
class MembersView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='members.index',
        renderer='members/index.mako'
        )
    def index(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Member)\
                .join(Membership, Membership.member_id==Member.id)\
                .join(MemberKind, MemberKind.id==Membership.member_kind_id)\
                .join(MemberSet, MemberSet.id==Member.member_set_id)\
                .filter(MemberSet.organization_id==self.request.operator.organization_id)\
                .order_by(Member.id)
        if self.request.params.get('member_set_id'):
                query = query.filter(MemberSet.id==self.request.params.get('member_set_id'))
        if self.request.params.get('member_kind_id'):
                query = query.filter(MemberKind.id==self.request.params.get('member_kind_id'))
        if self.request.params.get('search_name'):
                query = query.filter(Member.name.like(u"%%%s%%" % self.request.params.get('search_name')))
        if self.request.params.get('search_auth_identifier'):
                query = query.filter(Member.auth_identifier==self.request.params.get('search_auth_identifier'))
        if self.request.params.get('search_tel_1'):
                query = query.filter(Member.tel_1==self.request.params.get('search_tel_1'))

        members = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
            )
        member_sets = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id).all()
        member_kinds = session.query(MemberKind).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id).all()
        form = MemberForm(
            auth_secret=u'',
            request=self.request
            )
        return dict(
            members=members,
            member_sets=member_sets,
            member_kinds=member_kinds,
            form=form,
            )

    @view_config(
        route_name='members.edit',
        renderer='members/edit.mako',
        request_method='GET'
        )
    def edit(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Member).join(Member.member_set).filter_by(organization_id=self.request.operator.organization_id)
        member = query.filter(Member.id == self.request.matchdict['id']).one()
        form = MemberForm(
            obj=member,
            auth_secret=u'',
            request=self.request
            )
        return dict(
            form=form
            )

    @view_config(
        route_name='members.edit',
        renderer='members/edit.mako',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Member).join(Member.member_set).filter_by(organization_id=self.request.operator.organization_id)
        member = query.filter(Member.id == self.request.matchdict['id']).one()
        form = MemberForm(formdata=self.request.POST, obj=member, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member.member_set_id = form.member_set_id.data
        member.name = form.name.data
        member.auth_identifier = form.auth_identifier.data
        if form.auth_secret.data:
            member.auth_secret = digest_secret(form.auth_secret.data, generate_salt())
        member.email = form.email.data
        member.given_name = form.given_name.data
        member.family_name = form.family_name.data
        member.given_name_kana = form.given_name_kana.data
        member.family_name_kana = form.family_name_kana.data
        member.birthday = form.birthday.data
        member.gender = form.gender.data
        member.country = form.country.data
        member.zip = form.zip.data
        member.prefecture = form.prefecture.data
        member.city = form.city.data
        member.address_1 = form.address_1.data
        member.address_2 = form.address_2.data
        member.tel_1 = form.tel_1.data
        member.tel_2 = form.tel_2.data
        member.enabled = form.enabled.data
        memberships = {
            membership.id: membership
            for membership in member.memberships
            }
        deleted_memberships = set(member.memberships)
        for membership_id, membership_elem_list in form.memberships.entries.items():
            for membership_elem in membership_elem_list:
                membership_form = membership_elem._contained_form
                if membership_form.member_kind_id.data is not None:
                    if membership_id != form.memberships.placeholder_subfield_name:
                        membership = memberships[long(membership_id)]
                        deleted_memberships.remove(membership)
                    else:
                        membership = Membership(member_id=member.id)
                        session.add(membership)
                    membership_form.populate_obj(membership)
        for deleted_membership in deleted_memberships:
            session.delete(deleted_membership)
        session.add(member)
        session.commit()
        self.request.session.flash(u'会員 (Member) %s を変更しました' % member.name)
        return HTTPFound(location=self.request.route_path('members.edit', id=member.id))

    @view_config(
        route_name='members.new',
        renderer='members/new.mako',
        request_method='GET'
        )
    def new(self):
        form = MemberForm(request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='members.new',
        renderer='members/new.mako',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = MemberForm(formdata=self.request.POST, new_form=True, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member_set = session.query(MemberSet).filter_by(id=form.member_set_id.data).one()
        member = create_member(
            self.request,
            member_set=member_set,
            name=form.name.data,
            auth_identifier=form.auth_identifier.data,
            auth_secret=form.auth_secret.data,
            )
        member.email = form.email.data
        member.given_name = form.given_name.data
        member.family_name = form.family_name.data
        member.given_name_kana = form.given_name_kana.data
        member.family_name_kana = form.family_name_kana.data
        member.birthday = form.birthday.data
        member.gender = form.gender.data
        member.country = form.country.data
        member.zip = form.zip.data
        member.prefecture = form.prefecture.data
        member.city = form.city.data
        member.address_1 = form.address_1.data
        member.address_2 = form.address_2.data
        member.tel_1 = form.tel_1.data
        member.tel_2 = form.tel_2.data
        member.enabled = form.enabled.data
        for membership_id, membership_elem_list in form.memberships.entries.items():
            for membership_elem in membership_elem_list:
                membership_form = membership_elem._contained_form
                if membership_form.member_kind_id.data is not None:
                    if membership_id == form.memberships.placeholder_subfield_name:
                        membership = Membership()
                        membership_form.populate_obj(membership)
                        member.memberships.append(membership)
        session.add(member)
        session.commit()
        self.request.session.flash(u'会員 (Member) %s を作成しました' % member.auth_identifier)
        return HTTPFound(location=self.request.route_path('members.index'))

    @view_config(route_name='members.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        id_list = [r for r, in session.query(Member.id).join(Member.member_set).filter_by(organization_id=self.request.operator.organization_id).filter(Member.id.in_(id_list)) ]
        query = session.query(Member).filter(Member.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d 会員 (Member) を削除しました' % n)
        return HTTPFound(location=self.request.route_path('members.index'))

    @view_config(route_name='members.bulk_add')
    def bulk_add(self):
        master_session = get_db_session(self.request, 'extauth')
        slave_session = get_db_session(self.request, 'extauth_slave')
        organization_id = self.request.operator.organization_id
        file_fs = self.request.POST['file']
        if file_fs is None:
            self.request.session.flash(u'ファイルを指定してください')
        else:
            try:
                num_records = import_export.MemberDataImporter(master_session, organization_id)(
                    import_export.MemberDataParser(slave_session, organization_id)(
                        import_export.TabularDataReader(file_fs.file, file_fs.filename, import_export.japanese_columns)
                        )
                    )
                master_session.commit()
                self.request.session.flash(u'%d件をインポートしました' % num_records)
            except import_export.MemberImportExportErrors as e:
                m = u'%s (%d行目)' % (e.errors[0].message, e.errors[0].line_num)
                if len(e.errors) > 1:
                    m += '。ほか%d個の問題がありました' % len(e.errors) - 1
                self.request.session.flash(u'%s (インポート件数:%d)' % (m, e.num_records))
        return HTTPFound(location=self.request.route_path('members.index'))

    @view_config(route_name='members.export')
    def export(self):
        master_session = get_db_session(self.request, 'extauth')
        slave_session = get_db_session(self.request, 'extauth_slave')
        type_ = self.request.matchdict.get('ext', 'csv')
        organization_id = self.request.operator.organization_id
        resp = Response(status=200)
        exporter = import_export.MemberDataExporter(self.request, slave_session, organization_id)
        writer = import_export.TabularDataWriter(resp.body_file, import_export.japanese_columns.values(), import_export.japanese_columns.keys(), type=type_)
        date_time_formatter = lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S").decode("ASCII")
        date_formatter = lambda dt: dt.strftime("%Y-%m-%d").decode("ASCII")
        resp.content_type = writer.preferred_mime_type
        if resp.content_type.startswith('text/'):
            resp.charset = 'Windows-31J' if writer.encoding.lower() == 'cp932' else writer.encoding
        num_records = import_export.MemberDataWriterAdapter(date_time_formatter, date_formatter)(writer, exporter, ignore_close_error=True)
        self.request.session.flash(u'%d件をエクスポートしました' % num_records)
        return resp

    @view_config(route_name='members.bulk_delete')
    def bulk_delete(self):
        master_session = get_db_session(self.request, 'extauth')
        slave_session = get_db_session(self.request, 'extauth_slave')
        organization_id = self.request.operator.organization_id
        file_fs = self.request.POST['file']
        if file_fs is None:
            self.request.session.flash(u'ファイルを指定してください')
        else:
            try:
                num_records = import_export.MemberDeleteImporter(master_session, organization_id)(
                    import_export.MemberDataParser(slave_session, organization_id)(
                        import_export.TabularDataReader(file_fs.file, file_fs.filename, import_export.japanese_columns)
                        )
                    )
                master_session.commit()
                self.request.session.flash(u'%d件を削除しました' % num_records)
            except import_export.MemberImportExportErrors as e:
                m = u'%s (%d行目)' % (e.errors[0].message, e.errors[0].line_num)
                if len(e.errors) > 1:
                    m += '。ほか%d個の問題がありました' % len(e.errors) - 1
                self.request.session.flash(u'%s (削除件数:%d)' % (m, e.num_records))
        return HTTPFound(location=self.request.route_path('members.index'))

@view_defaults(
    renderer='oauth_clients/index.mako',
    decorator=(with_bootstrap),
    permission='manage_clients'
    )
class OAuthClientsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='oauth_clients.index',
        request_method='GET',
        )
    def index(self):
        oauth_clients = get_object_queryset(request=self.request, klass=OAuthClient)
        form = OAuthClientForm(request=self.request, organization_id=self.request.operator.organization_id)
        if self.request.operator.is_administrator or self.request.operator.is_superoperator:
            oauth_clients = oauth_clients.all()
        else:
            raise HTTPForbidden()
        return dict(
            oauth_clients=oauth_clients,
            form=form
            )

    def serialize(self, obj):
        columns = [c.key for c in class_mapper(obj.__class__).columns]
        serialized = dict()
        for c in columns:
            c_obj = getattr(obj, c)
            if isinstance(c_obj, (datetime.datetime, datetime.date)):
                serialized[c]=c_obj.isoformat()
            else:
                serialized[c] = c_obj
        return serialized

    @view_config(route_name='oauth_clients.create_or_update', request_method='POST', renderer="json")
    def create_or_update(self):
        oauth_client_id = self.request.POST.get('oauth_client_id', None)
        oauth_client_form = OAuthClientForm(self.request.POST, request=self.request)
        session = get_db_session(self.request, 'extauth')
        if oauth_client_id:
            try:
                oauth_client = session.query(OAuthClient).filter_by(id=oauth_client_id).one()
            except NoResultFound:
                raise HTTPBadRequest(body=json.dumps({'emsgs': {"unknown-emsg":u"該当OAuth Clientは見つからない。"}}))
        else:
            organization = lookup_organization_by_id(self.request, oauth_client_form.organization_id.data)
            oauth_client = OAuthClient()
            oauth_client.organization = organization
            oauth_client.client_id = generate_random_alnum_string(32)
            oauth_client.client_secret = generate_random_alnum_string(32)
            oauth_client.authorized_scope = organization.maximum_oauth_scope

        if not oauth_client_form.validate():
            emsgs = {}
            for field, errors in oauth_client_form.errors.items():
                for error in errors:
                    emsgs[field] = error
            raise HTTPBadRequest(body=json.dumps({'emsgs': emsgs}))

        oauth_client_form.populate_obj(oauth_client)
        try:
            session.add(oauth_client)
            session.commit()
        except Exception, e:
            raise HTTPBadRequest(body=json.dumps({'emsgs': {"unknown-emsg":str(e)}}))

        serialized_obj = self.serialize(oauth_client)
        return serialized_obj

    @view_config(route_name='oauth_clients.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        query = session.query(OAuthClient.id).filter(OAuthClient.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d OAuthClient を削除しました' % n)
        return HTTPFound(location=self.request.route_path('oauth_clients.index'))


@view_defaults(
    decorator=(with_bootstrap,),
    permission='manage_service_providers'
    )
class OAuthServiceProvidersView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='service_providers.index',
        renderer='service_providers/index.mako',
        request_method='GET',
        permission='manage_service_providers'
        )
    def index(self):
        service_providers = get_object_queryset(request=self.request, klass=OAuthServiceProvider)
        if self.request.operator.is_administrator or self.request.operator.is_superoperator:
            service_providers = service_providers.all()
        else:
            raise HTTPForbidden()
        return dict(
            service_providers=service_providers
            )

    @view_config(
        route_name='service_providers.new',
        renderer='service_providers/edit.mako',
        request_method='GET',
        permission='manage_service_providers'
        )
    def new(self):
        form = OAuthServiceProviderForm(request=self.request, organization_id=self.request.operator.organization_id)
        return dict(
            form=form
            )

    @view_config(
        route_name='service_providers.new',
        renderer='service_providers/edit.mako',
        request_method='POST',
        permission='manage_service_providers'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = OAuthServiceProviderForm(formdata=self.request.POST, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        service_provider = OAuthServiceProvider(
            name=form.name.data,
            display_name=form.display_name.data,
            auth_type=form.auth_type.data,
            endpoint_base=form.endpoint_base.data,
            consumer_key=form.consumer_key.data,
            consumer_secret=form.consumer_secret.data,
            scope=form.scope.data,
            organization_id=form.organization_id.data,
            visible=form.visible.data
        )
        session.add(service_provider)
        session.commit()
        self.request.session.flash(u'OAuthServiceProvider %s を新規作成しました' % service_provider.display_name)
        return HTTPFound(location=self.request.route_path('service_providers.edit', id=service_provider.id))

    @view_config(
        route_name='service_providers.edit',
        renderer='service_providers/edit.mako',
        request_method='GET'
        )
    def edit(self):
        service_provider = get_object_queryset(request=self.request, klass=OAuthServiceProvider)
        try:
            service_provider = service_provider.filter_by(id=self.request.matchdict['id']).one()
        except NoResultFound:
            raise HTTPForbidden()

        form = OAuthServiceProviderForm(obj=service_provider, request=self.request)
        return dict(
            form=form
            )

    @view_config(
        route_name='service_providers.edit',
        renderer='service_providers/edit.mako',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        service_provider = get_object_queryset(request=self.request, klass=OAuthServiceProvider, db_session=session)
        try:
            service_provider = service_provider.filter_by(id=self.request.matchdict['id']).one()
        except NoResultFound:
            raise HTTPForbidden()
        form = OAuthServiceProviderForm(formdata=self.request.POST, obj=service_provider, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        form.populate_obj(service_provider)
        session.commit()
        self.request.session.flash(u'OAuthServiceProvider %s を変更しました' % service_provider.display_name)
        return HTTPFound(location=self.request.route_path('service_providers.edit', id=service_provider.id))
