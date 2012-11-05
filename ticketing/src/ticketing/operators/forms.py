# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, DateField, PasswordField, SelectMultipleField
from wtforms.validators import Length, Email, Optional

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.operators.models import OperatorRole, Permission
from ticketing.models import DBSession

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
            Length(4, 32, message=u'4文字以上32文字以内で入力してください'),
        ]
    )
    password = PasswordField(
        label=u'パスワード',
        validators=[
            Length(4, 32, message=u'4文字以上32文字以内で入力してください'),
        ]
    )

    role_ids = SelectMultipleField(
        label=u'権限',
        validators=[Optional()],
        choices=[(role.id, role.name) for role in OperatorRole.all()],
        coerce=int,
    )
