# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class NewsLettersForm(Form):
    subject             = TextField(u'件名', validators=[Required()])
    description         = TextAreaField(u'本文', validators=[Required()])
    subscriber_count    = TextField(u'送信件数', validators=[])
    choices             = [('waiting', u'未送信'), ('complete', u'送信済')]
    status              = SelectField(u'状態', validators=[], choices = choices, default = '1')
    start_on            = DateField(u'送信日', validators=[Required()])
    subscriber_file     = FileField(u'送信先リスト', validators=[])
