# encoding: utf-8

import logging
from datetime import timedelta
from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget
from pyramid_layout.panel import panel_config
from webhelpers import paginate
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.sqlahelper import get_db_session
from .api import create_operator, lookup_operator_by_credentials
from ..models import MemberSet, MemberKind, Member, Membership, OAuthClient
from ..api import create_member
from ..utils import digest_secret, generate_salt, generate_random_alnum_string
from .forms import LoginForm, OperatorForm, MemberSetForm, MemberKindForm, MemberForm, OAuthClientForm
from .models import Operator
from . import import_export

logger = logging.getLogger(__name__)

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
    permission='manage_operators',
    decorator=(with_bootstrap,)
    )
class OperatorsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='operators.index',
        renderer='operators/index.mako'
        )
    def index(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Operator).filter_by(organization_id=self.request.operator.organization_id)
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
        request_method='GET'
        )
    def edit(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Operator).filter_by(organization_id=self.request.operator.organization_id)
        operator = query.filter_by(id=self.request.matchdict['id']).one()
        form = OperatorForm(
            auth_identifier=operator.auth_identifier,
            role=operator.role
            )
        return dict(
            form=form
            )

    @view_config(
        route_name='operators.edit',
        renderer='operators/edit.mako',
        request_method='POST'
        )
    def edit_post(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(Operator).filter_by(organization_id=self.request.operator.organization_id)
        operator = query.filter_by(id=self.request.matchdict['id']).one()
        form = OperatorForm(formdata=self.request.POST)
        if not form.validate():
            return dict(
                form=form
                )
        operator.role = form.role.data
        if form.auth_secret.data:
            operator.auth_secret = digest_secret(form.auth_secret.data, generate_salt())
        session.add(operator)
        session.commit()
        self.request.session.flash(u'オペレーター %s を変更しました' % operator.auth_identifier)
        return HTTPFound(location=self.request.route_path('operators.edit', id=operator.id))

    @view_config(
        route_name='operators.new',
        renderer='operators/new.mako',
        request_method='GET'
        )
    def new(self):
        form = OperatorForm()
        return dict(
            form=form
            )

    @view_config(
        route_name='operators.new',
        renderer='operators/new.mako',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = OperatorForm(formdata=self.request.POST, new_form=True, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        operator = create_operator(
            self.request,
            organization=self.request.operator.organization,
            auth_identifier=form.auth_identifier.data,
            auth_secret=form.auth_secret.data,
            role=form.role.data
            )
        session.commit()
        self.request.session.flash(u'オペレーター %s を作成しました' % operator.auth_identifier)
        return HTTPFound(location=self.request.route_path('operators.index'))

    @view_config(route_name='operators.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        if self.request.operator.id in id_list:
            self.request.session.flash(u'オペレーター %s は現在ログイン中のユーザのため削除できません' % self.request.operator.auth_identifier)
            return HTTPFound(location=self.request.route_path('operators.index'))
        query = session.query(Operator).filter_by(organization_id=self.request.operator.organization_id).filter(Operator.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d オペレーターを削除しました' % n)
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
        session.add(member_set)
        session.commit()
        self.request.session.flash(u'会員種別 %s を変更しました' % member_set.name)
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
            use_password=form.use_password.data
            )
        session.add(member_set)
        session.commit()
        self.request.session.flash(u'会員種別 %s を作成しました' % member_set.name)
        return HTTPFound(location=self.request.route_path('member_sets.index'))

    @view_config(route_name='member_sets.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        query = session.query(MemberSet).filter_by(organization_id=self.request.operator.organization_id).filter(MemberSet.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d 会員種別を削除しました' % n)
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
        self.request.session.flash(u'会員区分 %s を変更しました' % member_kind.name)
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
        self.request.session.flash(u'会員区分 %s を作成しました' % member_kind.name)
        return HTTPFound(location=self.request.route_path('member_kinds.index'))

    @view_config(route_name='member_kinds.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        id_list = [r for r, in session.query(MemberKind.id).join(MemberKind.member_set).filter_by(organization_id=self.request.operator.organization_id).filter(MemberKind.id.in_(id_list)) ]
        query = session.query(MemberKind).filter(MemberKind.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d 会員区分を削除しました' % n)
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
        query = session.query(Member).join(Member.member_set).filter_by(organization_id=self.request.operator.organization_id)
        members = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=paginate.PageURL_WebOb(self.request)
            )
        return dict(
            members=members
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
        form = MemberForm(formdata=self.request.POST, request=self.request)
        if not form.validate():
            return dict(
                form=form
                )
        member.member_set_id = form.member_set_id.data
        member.name = form.name.data
        member.auth_identifier = form.auth_identifier.data
        if form.auth_secret.data:
            member.auth_secret = digest_secret(form.auth_secret.data, generate_salt())
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
        self.request.session.flash(u'会員 %s を変更しました' % member.name)
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
            enabled=form.enabled.data
            )
        session.add(member)
        session.commit()
        self.request.session.flash(u'会員 %s を作成しました' % member.auth_identifier)
        return HTTPFound(location=self.request.route_path('members.index'))

    @view_config(route_name='members.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        id_list = [r for r, in session.query(Member.id).join(Member.member_set).filter_by(organization_id=self.request.operator.organization_id).filter(Member.id.in_(id_list)) ]
        query = session.query(Member).filter(Member.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d 会員を削除しました' % n)
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
                num_records = import_export.MemberCSVImporter(master_session, organization_id)(
                    import_export.MemberCSVParser(slave_session, organization_id)(
                        import_export.CSVReader(file_fs.file, import_export.japanese_columns)
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


@view_defaults(
    permission='manage_oauth_clients',
    decorator=(with_bootstrap,)
    )
class OAuthClientsView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        route_name='oauth_clients.index',
        renderer='oauth_clients/index.mako'
        )
    def index(self):
        session = get_db_session(self.request, 'extauth')
        query = session.query(OAuthClient).filter_by(organization_id=self.request.operator.organization_id)
        return dict(
            oauth_clients=query
            )

    @view_config(
        route_name='oauth_clients.new',
        renderer='oauth_clients/_new.mako',
        request_method='GET'
        )
    @panel_config(
        'oauth_clients.new',
        renderer='oauth_clients/_new.mako'
        )
    def new(self):
        form = OAuthClientForm()
        return dict(form=form)

    @view_config(
        route_name='oauth_clients.new',
        renderer='oauth_clients/_new.mako',
        request_method='POST'
        )
    def new_post(self):
        session = get_db_session(self.request, 'extauth')
        form = OAuthClientForm(self.request.POST)
        if not form.validate():
            self.request.response.status = 400
            return dict(form=form)
        valid_since = self.request.now
        organization = self.request.operator.organization
        oauth_client = OAuthClient(
            organization_id=organization.id,
            name=form.name.data,
            client_id=generate_random_alnum_string(32),
            client_secret=generate_random_alnum_string(32),
            redirect_uri=form.redirect_uri.data,
            authorized_scope=organization.maximum_oauth_scope,
            valid_since=valid_since,
            expire_at=valid_since + timedelta(seconds=organization.maximum_oauth_client_expiration_time)
            )
        session.add(oauth_client)
        session.commit()
        self.request.session.flash(u'OAuthアカウントを作成しました')
        return HTTPFound(location=self.request.route_path('oauth_clients.index'))

    @view_config(route_name='oauth_clients.delete')
    def delete(self):
        session = get_db_session(self.request, 'extauth')
        id_list = [long(id) for id in self.request.params.getall('id')]
        query = session.query(OAuthClient.id).filter_by(organization_id=self.request.operator.organization_id).filter(OAuthClient.id.in_(id_list))
        n = query.delete(False)
        session.commit()
        self.request.session.flash(u'%d アカウントを削除しました' % n)
        return HTTPFound(location=self.request.route_path('oauth_clients.index'))
