# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, HiddenField, SelectField
from wtforms.validators import Length, Optional, ValidationError

from altair.formhelpers import Translations, Required, BugFreeSelectField,\
    zero_as_none
from altair.app.ticketing.core.models import Organization, Account, AccountTypeEnum


class AccountSearchForm(Form):
    account_name = TextField(
        label=u'取引先名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )


class AccountForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.organization_id = kwargs['organization_id']

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    account_type = SelectField(
        label=u'取引先区分',
        validators=[Required()],
        choices=[account_type.v for account_type in AccountTypeEnum],
        coerce=int
    )
    name = TextField(
        label=u'取引先名',
        validators=[
            Required(),
            Length(max=255, message=u'255文字以内で入力してください'),
        ]
    )

    def validate_user_id(form, field):
        if field.data and not form.id.data:
            conditions = {
                'user_id': field.data,
                'organization_id':form.organization_id
            }
            if Account.filter_by(**conditions).first():
                raise ValidationError(u'既に登録済みの取引先です')
