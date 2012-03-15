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
    password    = PasswordField(u'パスワード'    , validators=[Required(),Length(4,32)])

class OperatorForm(Form):

    login_id    = TextField(u'ログインID'         , validators=[Required()])
    name        = TextField(u'名前'               , validators=[Required()])
    email       = TextField(u'Email'            , validators=[Required(), Email()])
    password    = PasswordField(u'パスワード'    , validators=[Length(4,32),optional()])
    password2   = PasswordField(u'パスワード確認' , validators=[
                                                        EqualTo('password', message=u'パスワードと確認用パスワードは一致しません。',)])


class AuthorizeForm(LoginForm):
    pass
