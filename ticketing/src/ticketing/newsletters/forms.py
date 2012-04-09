# -*- coding: utf-8 -*-

from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

class NewslettersForm(Form):
    subject             = TextField(u'件名', validators=[Required()])
    description         = TextAreaField(u'本文', validators=[Required()])
    subscriber_count    = TextField(u'送信件数', validators=[])
    choices             = [('editing', u'作成中'), ('waiting', u'送信予約中'), ('completed', u'送信完了')]
    status              = SelectField(u'状態', validators=[], choices=choices, default='editing')
    start_on            = DateField(u'送信日', validators=[Required()], format='%Y-%m-%d')
    start_at            = DateTimeField(u'送信時間', validators=[], format='%H:%M')
    subscriber_file     = FileField(u'送信先リスト', validators=[])
