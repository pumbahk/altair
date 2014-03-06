# -*- coding: utf-8 -*-

from wtforms import Form, ValidationError
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectMultipleField
from wtforms.validators import Length, Email, Optional, Regexp
from pyramid.security import has_permission, ACLAllowed

from altair.formhelpers import Translations, Required, PHPCompatibleSelectMultipleField
from altair.formhelpers.fields import DateTimeField
from altair.formhelpers.widgets import CheckboxMultipleSelect
from altair.app.ticketing.operators.models import Operator, OperatorAuth, OperatorRole, Permission
from altair.app.ticketing.permissions.utils import PermissionCategory
from altair.app.ticketing.models import DBSession

class OperatorRoleForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        if obj and obj.permissions:
            self.permissions.data = [p.category_name for p in obj.permissions]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'ロール名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    name_kana = TextField(
        label=u'ロール名(日本語表記)',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    permissions = PHPCompatibleSelectMultipleField(
        label=u"権限", 
        choices=lambda field: [(category_name, label) for category_name, label in PermissionCategory.items()],
        widget=CheckboxMultipleSelect(multiple=True)
    )

class OperatorForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if obj:
            self.login_id.data = obj.auth.login_id
            self.role_ids.data = [role.id for role in obj.roles]
            self.password.validators.append(Optional())
        else:
            self.password.validators.append(Required())
        if 'request' in kwargs:
            self.request = kwargs['request']

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    organization_id = HiddenField(
        validators=[Required()],
    )
    name = TextField(
        label=u'オペレーター名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    email = TextField(
        label=u'Email',
        validators=[
            Required(),
            Email(),
        ]
    )
    expire_at = DateTimeField(
        label=u'有効期限',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )

    login_id = TextField(
        label=u'ログインID',
        validators=[
            Required(),
            Length(4, 384, message=u'4文字以上384文字以内で入力してください'),
        ]
    )
    password = PasswordField(
        label=u'パスワード',
        validators=[
            Length(4, 32, message=u'4文字以上32文字以内で入力してください'),
            Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。'),
        ]
    )
    role_ids = PHPCompatibleSelectMultipleField(
        label=u'ロール',
        validators=[Optional()],
        choices=lambda field: [(role.id, role.name_kana) for role in OperatorRole.all()],
        coerce=int,
        widget=CheckboxMultipleSelect(multiple=True)
    )

    def validate_login_id(form, field):
        operator_auth = OperatorAuth.get_by_login_id(field.data)
        if operator_auth is not None:
            if not form.id.data or operator_auth.operator_id != int(form.id.data):
                raise ValidationError(u'ログインIDが重複しています。')

    def validate_id(form, field):
        # administratorロールのオペレータはadministratorロールがないと編集できない
        if field.data:
            if not isinstance(has_permission('administrator', form.request.context, form.request), ACLAllowed):
                operator = Operator.filter_by(id=field.data).first()
                if 'administrator' in [(role.name) for role in operator.roles]:
                    raise ValidationError(u'このオペレータを編集する権限がありません')
