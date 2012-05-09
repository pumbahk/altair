# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField
from wtforms.validators import Required, Regexp, Length, Optional, ValidationError

from ticketing.utils import DateTimeField
from ticketing.venues.models import Venue
from ticketing.events.models import Account

class PerformanceForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.venue_id.choices = [
                (venue.id, venue.name) for venue in Venue.get_by_organization_id(kwargs['organization_id'])
            ]

    name = TextField(
        label=u'公演名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    code = TextField(
        label=u'公演コード',
        validators=[
            Required(u'入力してください'),
            Regexp(u'^[a-zA-Z0-9]*$', message=u'英数字のみ入力できます'),
            Length(max=12, message=u'12文字以内で入力してください'),
        ],
    )
    open_on = DateTimeField(
        label=u'開場',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    start_on = DateTimeField(
        label=u'開演',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    end_on = DateTimeField(
        label=u'終演',
        validators=[Optional()],
        format='%Y-%m-%d %H:%M',
    )
    venue_id = SelectField(
        label=u'会場',
        validators=[Required(u'選択してください')],
        choices=[],
        coerce=int
    )

    def validate_start_on(form, field):
        if field.data and form.open_on.data and field.data < form.open_on.data:
            raise ValidationError(u'開場日時より過去の日時は入力できません')

    def validate_end_on(form, field):
        if field.data and form.start_on.data and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

class StockHolderForm(Form):
    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'organization_id' in kwargs:
            self.account_id.choices = [
                (account.id, account.name) for account in Account.get_by_organization_id(kwargs['organization_id'])
            ]

    name = TextField(
        label=u'枠名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
    account_id = SelectField(
        label=u'配券先',
        validators=[Required(u'入力してください')],
        choices=[],
        coerce=int
    )
    text            = TextField(u'記号', validators=[Required()])
    text_color      = TextField(u'記号色', validators=[Required()])
    fill_color      = TextField(u'色', validators=[Required()])
    fill_type       = SelectField(u'塗りつぶしパターン', validators=[Optional()], choices=[])
    fill_image      = TextField(u'塗りつぶしイメージ', validators=[Required()])
    stroke_color    = SelectField(u'線の色', validators=[Optional()], choices=[])
    stroke_width    = SelectField(u'線の太さ', validators=[Optional()], choices=[])
    stroke_patten   = SelectField(u'線の種類', validators=[Optional()], choices=[])
