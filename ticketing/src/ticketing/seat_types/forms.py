# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField, RadioField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional

class SeatTypeForm(Form):
    name            = TextField(u'名称', validators=[Required()])
    signature       = TextField(u'記号', validators=[Required()])
    fill_color      = TextField(u'色', validators=[Required()])
    line_color      = TextField(u'線色', validators=[Required()])
    line_thickness  = RadioField(u'線太さ', validators=[Required()])
    line_style      = RadioField(u'線種', validators=[Required()])
