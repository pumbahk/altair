# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, DateField
from wtforms.validators import Required, Length, Email, Optional

from ticketing.utils import DateTimeField, Translations
from ticketing.master.models import Prefecture

class OperatorRole(Form):
    pass

class OperatorRoleForm(Form):
    pass

class OperatorForm(Form):

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    organization_id = HiddenField(
        validators=[Required(u'入力してください')],
    )
    name = TextField(
        label=u'名前',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )
    email = TextField(
        label=u'Email',
        validators=[
            Required(u'入力してください'),
            Email(),
        ]
    )
    expire_at = DateTimeField(
        label=u'有効期限',
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M',
    )
