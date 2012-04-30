# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional

class AccountForm(Form):
    name = TextField(u'クライアント名', validators=[
        Required(u'入力してください'),
        Length(max=255, message=u'255文字以内で入力してください'),
        ])
