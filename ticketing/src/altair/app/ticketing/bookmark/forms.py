# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import (TextField, PasswordField, TextAreaField, DateField, DateTimeField,
                     SelectField, SubmitField, HiddenField, BooleanField, FileField)
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional,url as Url

class BookmarkForm(Form):
    name = TextField(u'開演日時', validators=[
        Required(u'入力してください'),
        ])
    url = TextField(u'最終公演日時', validators=[
        Required(u'入力してください'),
        Url(u'URLを正しく入力してください'),
        ])
