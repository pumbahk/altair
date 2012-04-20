# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, SelectField,
                     SubmitField, HiddenField, BooleanField, FileField, IntegerField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms.widgets import Select
from ticketing.venues.models import Venue

class PerformanceForm(Form):
    name     = TextField(u'公演名', validators=[Required(u'入力してください')])
    code     = TextField(u'公演コード', validators=[Required(u'入力してください')])
    open_on  = DateField(u'開場', validators=[Required(u'入力してください')], format='%Y-%m-%d %H:%M:%S')
    start_on = DateField(u'開演', validators=[Required(u'入力してください')], format='%Y-%m-%d %H:%M:%S')
    end_on   = DateField(u'終演', validators=[], format='%Y-%m-%d %H:%M:%S')
    venue_id = SelectField(u'会場', validators=[Required(u'選択してください')],
                           choices=[(venue.id, venue.name) for venue in Venue.all()], coerce=int)

