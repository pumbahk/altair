# encoding: utf-8

import itertools
from datetime import timedelta
from urlparse import urlparse
from sqlalchemy.orm.exc import NoResultFound
from altair.formhelpers.form import OurForm
from altair.formhelpers.filters import blank_as_none
from altair.formhelpers.fields import (
    OurTextField,
    OurSelectField,
    OurSelectMultipleField,
    OurGenericFieldList,
    OurFormField,
    OurIntegerField,
    OurBooleanField,
    OurHiddenField,
    NestableElementNameHandler,
)
from altair.formhelpers.fields.datetime import (
    OurDateTimeField,
    OurDateField,
    )
from altair.formhelpers.widgets import (
    OurPasswordInput,
    OurTextInput,
    OurDateWidget,
)
from altair.formhelpers.fields.select import SimpleChoices
from altair.formhelpers.validators import (
    RequiredOnNew,
    Zenkaku,
    Katakana,
    )
from altair.formhelpers.validators.optional import SwitchOptionalBase
from altair.formhelpers import Max, after1900
from wtforms.validators import Required, Length, Optional
from wtforms import ValidationError
from altair.sqlahelper import get_db_session
from ..models import MemberSet, MemberKind, Member, Host, Organization, OAuthServiceProvider
from .models import Role
from ..utils import period_overlaps
from ..interfaces import ICommunicator
from .api import lookup_operator_by_auth_identifier

ONE_SECOND = timedelta(seconds=1)

class LoginForm(OurForm):
    user_name = OurTextField(
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    password = OurTextField(
        widget=OurPasswordInput(),
        validators=[
            Required()
            ]
        )


class DictBackedFormField(OurFormField):
    def fetch_value_from_obj(self, obj, name):
        candidate = obj.get(name, None)
        if candidate is None:
            if self._obj is None:
                raise TypeError('fetch_value_from_obj: cannot find a value to populate from the provided obj or input data/defaults')
            candidate = self._obj
        return candidate[name]

    def populate_obj(self, obj, name):
        candidate = obj.get(name, None)
        if candidate is None:
            if self._obj is None:
                raise TypeError('populate_obj: cannot find a value to populate from the provided obj or input data/defaults')
            candidate = self._obj
            obj[name] = candidate
        self.form.populate_obj(candidate)


class DictBackedForm(OurForm):
    def populate_obj(self, obj):
        for name, field in self._fields.items():
            obj[name] = field.data


class RakutenAuthSettingsForm(DictBackedForm):
    oauth_consumer_key = OurTextField(
        label=u'OAuth Consumer Key',
        filters=[blank_as_none]
        )

    oauth_consumer_secret = OurTextField(
        label=u'OAuth Consumer Secret',
        filters=[blank_as_none]
        )

    proxy_url_pattern = OurTextField(
        label=u'Proxy URL pattern',
        filters=[blank_as_none]
        )
    


class OrganizationSettingsForm(DictBackedForm):
    rakuten_auth = DictBackedFormField(RakutenAuthSettingsForm)


class OrganizationForm(OurForm):
    short_name = OurTextField(
        label=u'ショートネーム',
        validators=[Required()]
        )

    maximum_oauth_scope = OurSelectMultipleField(
        label=u'デフォルトOAuthスコープ',
        choices=[
            (u'user_info', u'user_info'),
            ],
        default=[u'user_info']
        )

    canonical_host_name = OurSelectField(
        label=u'正規ホスト名',
        choices=lambda field: \
            get_db_session(field._form.request, 'extauth') \
                .query(Host.host_name, Host.host_name) \
                .filter(Host.organization_id == field._form.organization_id) \
                .all()
        )

    fanclub_api_available = OurBooleanField(
        label=u'ファンクラブAPI有効化'
        )

    invalidate_client_http_session_on_access_token_revocation = OurBooleanField(
        label=u'アクセストークンの無効化時にHTTPセッションも無効化する'
        )

    emergency_exit_url = OurTextField(
        label=u'致命的エラー時の脱出先URL',
        filters=[blank_as_none]
        )

    fanclub_api_type = OurSelectField(
        label=u'ファンクラブAPIの種類',
        choices=lambda field: [(name, name) for name, _ in field._form.request.registry.getUtilitiesFor(ICommunicator)],
        validators=[
            SwitchOptionalBase(predicate=lambda form, field: not form.is_fanclub_api_available),
            ]
        )

    settings = OurFormField(OrganizationSettingsForm)

    @property
    def is_fanclub_api_available(self):
        return self.request and self.request.operator and self.request.operator.organization.fanclub_api_available

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        organization = kwargs.get('obj', None)
        self.organization_id = organization.id if organization else None
        super(OrganizationForm, self).__init__(*args, **kwargs)


class HostForm(OurForm):
    host_name = OurTextField(
        label=u'ホスト名',
        validators=[Required()]
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(HostForm, self).__init__(*args, **kwargs)


class OperatorForm(OurForm):
    auth_identifier = OurTextField(
        label=u'ログインID',
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    auth_secret = OurTextField(
        label=u'パスワード',
        widget=OurPasswordInput(),
        validators=[
            RequiredOnNew()
            ]
        )

    auth_secret_confirm = OurTextField(
        label=u'パスワード (確認)',
        widget=OurPasswordInput(),
        validators=[]
        )

    role_id = OurSelectField(
        label=u'役割',
        choices=[
            (1, u'管理者'),
            (2, u'スーパーオペレーター'),
            (3, u'オペレーター'),
            ],
        validators=[
            Required(),
            ],
        coerce=int
        )

    organization_id = OurSelectField(
        label=u'所属組織',
        choices=lambda field: \
            get_db_session(field._form.request, 'extauth_slave') \
                .query(Organization.id, Organization.short_name) \
                .all(),
        validators=[
            Required(),
            ],
        coerce=int
        )

    def validate_auth_secret_confirm(form, field):
        if form.auth_secret.data != '' and field.data != form.auth_secret.data:
            raise ValidationError(u'パスワードが一致しません')

    def validate_auth_identifier(form, field):
        operator = lookup_operator_by_auth_identifier(form.request, field.data) 
        if form.new_form:
            if operator is None:
                return
        else:
            if operator is None or operator.id == form._obj.id:
                return
        raise ValidationError(u'同じログインIDがすでに登録されています')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self._obj = kwargs.get('obj')
        super(OperatorForm, self).__init__(*args, **kwargs)
        if not self.request.operator.is_administrator:
            self.role_id.choices = [choice for choice in self.role_id.choices[1:]]



class MemberSetForm(OurForm):
    name = OurTextField(
        label=u'名称',
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    display_name = OurTextField(
        label=u'表示名称',
        validators=[
            Required(),
            Length(max=255)
            ]
        )

    applicable_subtype = OurTextField(
        label=u'サブタイプ指定',
        filters=[blank_as_none],
        validators=[
            Length(max=255)
            ]
        )

    use_password = OurBooleanField(
        label=u'パスワードを利用する',
        default=True
        )

    auth_identifier_field_name = OurTextField(
        label=u'「ログイン名」フィールドの名称',
        filters=[blank_as_none],
        validators=[
            Length(max=255)
            ]
        )

    auth_secret_field_name = OurTextField(
        label=u'「パスワード」フィールドの名称',
        filters=[blank_as_none],
        validators=[
            Length(max=255)
            ]
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MemberSetForm, self).__init__(*args, **kwargs)


class MemberKindForm(OurForm):
    member_set_id = OurSelectField(
        label=u'会員種別',
        choices=lambda field: [
            (member_set.id, member_set.name) \
            for member_set in \
                get_db_session(field._form.request, 'extauth').query(MemberSet) \
                    .filter_by(organization_id=field._form.request.operator.organization_id)
            ],
        coerce=int,
        validators=[]
        )

    name = OurTextField(
        label=u'名称',
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    display_name = OurTextField(
        label=u'表示名称',
        validators=[
            Required(),
            Length(max=255)
            ]
        )

    show_in_landing_page = OurBooleanField(
        label=u'ランディングページに表示',
        default=True
        )

    enable_guests = OurBooleanField(
        label=u'ゲストログインを有効にする',
        default=False
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MemberKindForm, self).__init__(*args, **kwargs)


class MembershipForm(OurForm):
    member_kind_id = OurSelectField( 
        model=lambda field: SimpleChoices(
            [(None, u'選択してください')] + [
                ((member_kind.member_set_id, member_kind.id), member_kind.name) \
                for member_kind in \
                    get_db_session(field._form.request,
                                   'extauth').query(MemberKind) \
                        .join(MemberKind.member_set) \
                        .filter_by(organization_id=field._form.request.operator.organization_id)
                ],
            encoder=lambda v: u'%d-%d' % v if v else u'',
            decoder=lambda v: tuple(long(i) for i in v.split(u'-', 2)) if v != u'' else None
            ),
        validators=[
            Required()
            ],
        obj_value_filter=(
            lambda field, member_kind_id: (
                get_db_session(field._form.request, 'extauth').query(MemberKind) \
                    .filter_by(id=member_kind_id).one().member_set_id,
                member_kind_id
                ),
            lambda field, pair: pair[1] if pair is not None else None
            )
        )

    membership_identifier = OurTextField(
        label=u'会員ID',
        filters=[blank_as_none],
        validators=[
            Optional()
            ]
        )

    valid_since = OurDateTimeField(
        label=u'有効化日時',
        format=u'%Y-%m-%d %H:%M'
        )

    expire_at = OurDateTimeField(
        label=u'有効期限',
        format=u'%Y-%m-%d %H:%M',
        missing_value_defaults=dict(hour=u'23', minute=u'59', second=u'59'),
        obj_value_filter=(
            lambda field, expire_at: \
                expire_at - ONE_SECOND if expire_at is not None
                                       else None,
            lambda field, expire_at: \
                expire_at + ONE_SECOND if expire_at is not None
                                       else None
            )
        )

    enabled = OurBooleanField(
        label=u'有効フラグ',
        default=True
        )

    def validate_member_kind_id(form, field):
        if field.data is not None:
            (member_set_id, member_kind_id) = field.data
            if member_set_id != form.toplevel_form.member_set_id.data:
                raise ValidationError(u'会員区分の選択に誤りがあります')

    @property
    def toplevel_form(self):
        return self._containing_field._form.form

    @property
    def request(self):
        return self.toplevel_form.request

    def __init__(self, *args, **kwargs):
        self._containing_field = kwargs.pop('_containing_field', None)
        super(MembershipForm, self).__init__(*args, **kwargs)


class MemberForm(OurForm):
    member_set_id = OurSelectField(
        label=u'会員種別',
        choices=lambda field: [
            (member_set.id, member_set.name) \
            for member_set in \
                get_db_session(field._form.request, 'extauth').query(MemberSet) \
                    .filter_by(organization_id=field._form.request.operator.organization_id)
            ],
        coerce=int,
        validators=[]
        )

    name = OurTextField(
        label=u'氏名',
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    auth_identifier = OurTextField(
        label=u'ログインID',
        validators=[
            Required(),
            Length(max=32)
            ]
        )

    auth_secret = OurTextField(
        label=u'パスワード',
        widget=OurPasswordInput(),
        validators=[
            RequiredOnNew()
            ]
        )

    auth_secret_confirm = OurTextField(
        label=u'パスワード (確認)',
        widget=OurPasswordInput(),
        validators=[]
        )

    memberships = OurGenericFieldList(
        label=u'会員区分',
        name_handler=NestableElementNameHandler(),
        placeholder_subfield_name=u'__placeholder__',
        unbound_field=OurFormField(MembershipForm),
        validators=[],
        obj_value_filter=lambda field, memberships: {
            unicode(membership.id): [membership]
            for membership in memberships
            }
        )

    email = OurTextField(
        label=u'メールアドレス',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    given_name = OurTextField(
        label=u'配送先名',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    family_name = OurTextField(
        label=u'配送先姓',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    given_name_kana = OurTextField(
        label=u'配送先名(カナ)',
        validators=[
            Optional(),
            Katakana,
            Length(max=255),
            ]
        )

    family_name_kana = OurTextField(
        label=u'配送先姓(カナ)',
        validators=[
            Optional(),
            Katakana,
            Length(max=255),
            ]
        )

    birthday = OurDateField(
        label=u'誕生日',
        validators=[
            Optional(),
            ]
        )

    gender = OurSelectField(
        label=u'性別',
        validators=[
            Optional(),
            ],
        model=SimpleChoices(
            [
                (None, u'(入力なし)'),
                (0, u'未回答'),
                (1, u'男性'),
                (2, u'女性')
                ],
            decoder=lambda x: int(x) if x != u'' else None,
            encoder=lambda x: unicode(x) if x is not None else u''
            )
        )

    country = OurTextField(
        label=u'国',
        validators=[
            Optional(),
            Length(max=64),
            ]
        )

    zip = OurTextField(
        label=u'郵便番号',
        validators=[
            Optional(),
            Length(max=32),
            ]
        )

    prefecture = OurTextField(
        label=u'都道府県',
        validators=[
            Optional(),
            Length(max=128),
            ]
        )

    city = OurTextField(
        label=u'市区町村',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    address_1 = OurTextField(
        label=u'住所1',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    address_2 = OurTextField(
        label=u'住所2',
        validators=[
            Optional(),
            Length(max=255),
            ]
        )

    tel_1 = OurTextField(
        label=u'電話番号1',
        validators=[
            Optional(),
            Length(max=32),
            ]
        )

    tel_2 = OurTextField(
        label=u'電話番号2',
        validators=[
            Optional(),
            Length(max=32),
            ]
        )

    enabled = OurBooleanField(
        label=u'有効フラグ',
        default=True
        )

    search_name = OurTextField(
        label=u'氏名(前後方一致)'
        )

    search_auth_identifier = OurTextField(
        label=u'ログインID(完全一致)'
        )

    search_tel_1 = OurTextField(
        label=u'電話番号(完全一致)'
        )

    def validate_auth_secret_confirm(form, field):
        if form.auth_secret.data != '' and field.data != form.auth_secret.data:
            raise ValidationError(u'パスワードが一致しません')

    def validate_auth_identifier(form, field):
        member = None
        try:
            member = get_db_session(form.request, 'extauth').query(Member).join(Member.member_set) \
                    .filter(Member.auth_identifier == field.data,
                            Member.member_set_id == form.member_set_id.data,
                            MemberSet.organization_id == form.request.operator.organization_id) \
                    .one()
        except NoResultFound:
            pass
        if form.new_form:
            if member is None:
                return
        else:
            if member is None or member.id == form._obj.id:
                return
        raise ValidationError(u'同じログインIDがすでに登録されています')

    def validate_memberships(form, field):
        fields_by_member_kind = {}
        for subfield_name, subfields in field:
            for subfield in subfields:
                if subfield.member_kind_id.data is not None:
                    fields_by_member_kind.setdefault(subfield.member_kind_id.data[1], []).append(subfield)
        for member_kind_id, subfields in fields_by_member_kind.items():
            for a, b in itertools.combinations(subfields, 2):
                if period_overlaps(
                        (
                            a.valid_since.data,
                            (
                                a.expire_at.data + ONE_SECOND 
                                if a.expire_at.data is not None
                                else None
                                )
                            ),
                        (
                            b.valid_since.data,
                            (
                                b.expire_at.data + ONE_SECOND 
                                if b.expire_at.data is not None
                                else None
                                )
                            )
                        ):
                    member_kind = get_db_session(form.request, 'extauth') \
                        .query(MemberKind).filter_by(id=member_kind_id).one()
                    raise ValidationError(u'%sの有効期間が重なっています' % member_kind.name)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self._obj = kwargs.get('obj')
        super(MemberForm, self).__init__(*args, **kwargs)

class OAuthClientForm(OurForm):
    name = OurTextField(
        label=u'アプリケーション名称',
        validators=[
            Required(),
            Length(max=128)
            ]
        )

    redirect_uri = OurTextField(
        label=u'リダイレクトURI',
        validators=[
            Required(),
            Length(max=384)
            ]
        )

    organization_id = OurSelectField(
        label=u'組織名 (Organization)',
        choices=lambda field: \
            get_db_session(field._form.request, 'extauth_slave') \
                .query(Organization.id, Organization.short_name) \
                .all(),
        validators=[
            Required(),
            ],
        coerce=int
        )

    def validate_redirect_uri(form, field):
        parsed = None
        try:
            parsed = urlparse(field.data)
        except:
            pass
        if parsed is None or parsed.scheme not in ('http', 'https'):
            raise ValidationError(u'URIの形式が正しくありません')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OAuthClientForm, self).__init__(*args, **kwargs)


class OAuthServiceProviderForm(OurForm):
    name = OurTextField(
        label=u'OAuthプロバイダ名(英字)',
        validators=[
            Required(),
            Length(max=32)
            ]
        )
    organization_id = OurSelectField(
        label=u'Organization',
        choices=lambda field: \
            get_db_session(field._form.request, 'extauth_slave') \
                .query(Organization.id, Organization.short_name) \
                .all(),
        coerce=int,
        validators=[
            Required(),
            ]
        )
    display_name = OurTextField(
        label=u'OAuthプロバイダ名(表示名)',
        validators=[
            Required(),
            Length(max=255)
            ]
        )
    auth_type = OurSelectField(
        label=u'認証方式',
        choices=[(u'rakuten', u'楽天認証'), (u'pollux', u'Pollux認証')],
        validators=[
            Required()
            ]
        )
    endpoint_base = OurTextField(
        label=u'OAuthエンドポイント(Base URL)',
        validators=[
            Required(),
            Length(max=255)
            ]
        )
    consumer_key = OurTextField(
        label=u'OAuth Consumer Key',
        validators=[
            Required(),
            Length(max=255)
            ]
        )
    consumer_secret = OurTextField(
        label=u'OAuth Consumer Secret',
        validators=[
            Required(),
            Length(max=255)
            ]
        )
    scope = OurTextField(
        label=u'OAuthスコープ',
        validators=[
            Optional(),
            Length(max=255)
            ]
        )
    visible = OurBooleanField(
        label=u'公開',
        default=True
        )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OAuthServiceProviderForm, self).__init__(*args, **kwargs)

    def validate_name(form, field):
        sp = get_db_session(form.request, 'extauth') \
                .query(OAuthServiceProvider) \
                .filter(OAuthServiceProvider.organization_id == form.organization_id.data) \
                .filter(OAuthServiceProvider.name == field.data) \
                .first()
        # 同Org内で名前が重複しないようにする
        # editの時
        if form.request.matchdict.get('id'):
            if sp and sp.id != int(form.request.matchdict.get('id')):
                raise ValidationError(u'「%s」は同org内で既に使用されております' % field.data)
        # newの時
        else:
            if sp:
                raise ValidationError(u'「%s」は同org内で既に使用されております' % field.data)

