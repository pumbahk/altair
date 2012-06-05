# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, IntegerField, HiddenField, SelectField
from wtforms.validators import Regexp, Length, Optional, ValidationError

from ticketing.formhelpers import DateTimeField, Translations, Required
from ticketing.events.models import Event, Account

class EventForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'user_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.filter_by(user_id=kwargs['user_id'])
            ]

    def _get_translations(self):
        return Translations()

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    account_id = SelectField(
        label=u'クライアント',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )
    code = TextField(
        label = u'イベントコード',
        validators=[
            Required(),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'英数字のみ入力できます'),
            Length(min=6, max=6, message=u'6文字で入力してください'),
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
    start_on = DateTimeField(
        label = u'開演日時',
        validators=[Required()],
        format='%Y-%m-%d %H:%M'
    )
    end_on = DateTimeField(
        label = u'最終公演日時',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M'
    )

    def validate_end_on(form, field):
        if field.data is not None and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

    def validate_code(form, field):
        if form.id and form.id.data:
            return
        if field.data and Event.filter_by(code=field.data).count():
            raise ValidationError(u'既に使用されています')
