# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange, EqualTo, Optional
from wtforms.widgets import Select
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

