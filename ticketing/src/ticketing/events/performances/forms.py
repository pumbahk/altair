# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import TextField, SelectField
from wtforms.validators import Required, Regexp, Length, Optional

from ticketing.utils import DateTimeField
from ticketing.venues.models import Venue

class PerformanceForm(Form):
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
        validators=[Required(u'入力してください')],
        format='%Y-%m-%d %H:%M',
    )
    start_on = DateTimeField(
        label=u'開演',
        validators=[Required(u'入力してください')],
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
        choices=[(venue.id, venue.name) for venue in Venue.all()],
        coerce=int
    )

    def validate_start_on(form, field):
        if field.data is not None and field.data < form.open_on.data:
            raise ValidationError(u'開場日時より過去の日時は入力できません')

    def validate_end_on(form, field):
        if field.data is not None and field.data < form.start_on.data:
            raise ValidationError(u'開演日時より過去の日時は入力できません')

class StockHolderForm(Form):
    name = TextField(
        label=u'枠名',
        validators=[
            Required(u'入力してください'),
            Length(max=255, message=u'255文字以内で入力してください'),
        ],
    )
