# -*- coding: utf-8 -*-


from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class PerformanceForm(Form):
    open_on              =  DateField(u'開場', validators=[Required()])
    start_on            =  DateField(u'開演', validators=[Required()])
    end_on              =  DateField(u'終演', validators=[])
    code                = TextField(u'公演コード', validators=[Required()])
    title               = TextField(u'タイトル', validators=[Required()])
    abbreviated_title   = TextField(u'タイトル略', validators=[Required()])

