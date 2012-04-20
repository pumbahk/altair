# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, SelectField,
                     SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional

class EventForm(Form):
    code                = TextField(u'公演コード', validators=[Required(u'入力してください')])
    title               = TextField(u'タイトル', validators=[Required(u'入力してください')])
    abbreviated_title   = TextField(u'タイトル略称', validators=[Required(u'入力してください')])
    start_on            = DateField(u'開演日時', validators=[Required(u'入力してください')])
    end_on              = DateField(u'最終公演日時', validators=[Required(u'入力してください')])
