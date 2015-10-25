# encoding: utf-8

import itertools
from datetime import timedelta
from urlparse import urlparse
from altair.formhelpers.form import OurForm
from altair.formhelpers.filters import blank_as_none
from altair.formhelpers.fields import (
    OurTextField,
    OurSelectField,
    OurGenericFieldList,
    OurFormField,
    OurBooleanField,
    NestableElementNameHandler,
)
from altair.formhelpers.fields.datetime import (
    OurDateTimeField,
    )
from altair.formhelpers.widgets import (
    OurPasswordInput,
    OurTextInput,
    OurDateWidget,
)
from altair.formhelpers.fields.select import SimpleChoices
from altair.formhelpers.validators import RequiredOnNew
from altair.formhelpers import Max, after1900
from wtforms.validators import Required, Length, Optional
from wtforms import ValidationError
from altair.sqlahelper import get_db_session
from ..models import MemberSet, MemberKind, Member
from ..utils import period_overlaps
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

    role = OurSelectField(
        label=u'役割',
        choices=[
            (u'administrator', u'管理者'),
            (u'operator', u'オペレーター'),
            ],
        validators=[
            Required(),
            ]
        )

    def validate_auth_secret_confirm(form, field):
        if form.auth_secret.data != '' and field.data != form.auth_secret.data:
            raise ValidationError(u'パスワードが一致しません')

    def validate_auth_identifier(form, field):
        if form.new_form and form.request:
            if lookup_operator_by_auth_identifier(form.request, field.data) is not None:
                raise ValidationError(u'オペレータ %s はすでに登録されています' % field.data)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OperatorForm, self).__init__(*args, **kwargs)


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

    enabled = OurBooleanField(
        label=u'有効フラグ',
        default=True
        )

    def validate_auth_secret_confirm(form, field):
        if form.auth_secret.data != '' and field.data != form.auth_secret.data:
            raise ValidationError(u'パスワードが一致しません')

    def validate_auth_identifier(form, field):
        if form.new_form and form.request:
            if lookup_operator_by_auth_identifier(form.request, field.data) is not None:
                raise ValidationError(u'同じログインIDがすでに登録されています' % field.data)

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
