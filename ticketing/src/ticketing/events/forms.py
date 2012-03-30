# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class EventForm(Form):
    start_on            = DateField(u'開始日', validators=[Required()])
    end_on              = DateField(u'終了日', validators=[Required()])
    code                = TextField(u'公演コード', validators=[Required()])
    title               = TextField(u'タイトル', validators=[Required()])
    abbreviated_title   = TextField(u'タイトル略称', validators=[Required()])
