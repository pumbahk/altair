# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, TextAreaField, DateField, SelectField, SubmitField, HiddenField, BooleanField, FileField
from wtforms.validators import Required, Email, Length, NumberRange,EqualTo,optional
from wtforms import Form

from ticketing.models.master import Prefecture

class LoginForm(Form):
    '''
      Login form
    '''
    login_id    = TextField(u'ユーザー名'         , validators=[Required()])
    password    = PasswordField(u'パスワード'    , validators=[Required(),Length(8,32)])

class OperatorForm(Form):
    '''
    email       = TextField(u'ユーザー名'         , validators=[Required(),Email()])
    name        = TextField(u'名前'               , validators=[Required()])
    login_id    = SchemaNode(String()   , title=u'ログインID')
    secret_key  = SchemaNode(String()   , title=u'パスワード', missing=null, widget=CheckedPasswordWidget())
    '''
    pass
