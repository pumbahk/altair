# -*- coding: utf-8 -*-

from wtforms import Form, ValidationError
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectMultipleField
from wtforms.validators import Length, Email, Optional, Regexp
from pyramid.security import has_permission, ACLAllowed

from altair.formhelpers import Translations, Required
from altair.formhelpers.fields import DateTimeField, LazySelectMultipleField
from altair.app.ticketing.operators.models import Operator, OperatorAuth, OperatorRole, Permission
from altair.app.ticketing.models import DBSession

class OperatorRoleForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)

        category_names = DBSession.query(Permission.category_name).distinct().all()
        self.permissions.choices = [(name[0], name[0]) for name in category_names]
        if obj and obj.permissions:
            self.permissions.data = [p.category_name for p in obj.permissions]

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    name = TextField(
        label=u'名前',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    permissions = SelectMultipleField(
        label=u"権限", 
        choices=[]
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
        label=u'名前',
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

    role_ids = LazySelectMultipleField(
        label=u'権限',
        validators=[Optional()],
        choices=lambda field: [(role.id, role.name) for role in OperatorRole.all()],
        coerce=int,
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
