# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional

class EventForm(Form):
    code = TextField(u'公演コード', validators=[
        Required(u'入力してください'),
        Length(max=12, message=u'12文字以内で入力してください'),
        ])
    title = TextField(u'タイトル', validators=[
        Required(u'入力してください'),
        Length(max=200, message=u'200文字以内で入力してください'),
        ])
    abbreviated_title = TextField(u'タイトル略称', validators=[
        Required(u'入力してください'),
        Length(max=100, message=u'100文字以内で入力してください'),
        ])
    start_on = DateTimeField(u'開演日時', validators=[
        Required(u'入力してください'),
        ], format='%Y-%m-%d %H:%M')
    end_on = DateTimeField(u'最終公演日時', validators=[
        Required(u'入力してください'),
        ], format='%Y-%m-%d %H:%M')
