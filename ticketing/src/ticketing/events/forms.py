# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.core.models import Event, Account

class EventForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.filter_by(organization_id=kwargs['organization_id'])
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    account_id = SelectField(
        label=u'配券元',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    code = TextField(
        label = u'イベントコード',
        validators=[
            Required(),
            Regexp(u'^[A-Z0-9]*$', message=u'英数字大文字のみ入力できます'),
            Length(min=5, max=5, message=u'5文字で入力してください'),
        ]
    )
    title = TextField(
        label = u'タイトル',
        validators=[
            Required(),
            Length(max=200, message=u'200文字以内で入力してください'),
        ]
    )
    abbreviated_title = TextField(
        label = u'タイトル略称',
        validators=[
            Required(),
            Length(max=100, message=u'100文字以内で入力してください'),
        ]
    )
    original_id = HiddenField(
        validators=[Optional()],
    )

    def validate_code(form, field):
        if form.id and form.id.data:
            return
        if field.data and Event.filter_by(code=field.data).count():
            raise ValidationError(u'既に使用されています')
