# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class NewsLettersForm(Form):
    subject             = TextField(u'タイトル', validators=[Required()])
    description         = TextAreaField(u'本文', validators=[Required()])
    start_on            = DateField(u'送信開始日', validators=[Required()])
