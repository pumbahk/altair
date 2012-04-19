# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, SelectField,
                     SubmitField, HiddenField, BooleanField, FileField, IntegerField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms.widgets import Select
from ticketing.venues.models import Venue

class PerformanceForm(Form):
    name     = TextField(u'公演名', validators=[Required()])
    code     = TextField(u'公演コード', validators=[Required()])
    open_on  = DateField(u'開場', validators=[Required()])
    start_on = DateField(u'開演', validators=[Required()])
    end_on   = DateField(u'終演', validators=[])
    venue_id = SelectField(u'会場', validators=[],
                           choices=[(venue.id, venue.name) for venue in Venue.all()], coerce=int)


