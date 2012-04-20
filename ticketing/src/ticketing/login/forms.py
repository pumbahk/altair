# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, optional
from wtforms import Form

class LoginForm(Form):
    '''
      Login form
    '''
    login_id    = TextField(u'ユーザー名'         , validators=[Required(message=u'必須項目です。')])
    password    = PasswordField(u'パスワード'    , validators=[Required(message=u'必須項目です。'),Length(4,32,message=u'4文字以上32文字以内で入力してください。')])

class ResetForm(Form):
    email    = TextField(u'Email'         , validators=[Required(message=u'必須項目です。')])

class OperatorForm(Form):

    login_id    = TextField(u'ログインID'         , validators=[Required()])
    name        = TextField(u'名前'               , validators=[Required()])
    email       = TextField(u'Email'            , validators=[Required(), Email()])
    password    = PasswordField(u'パスワード'    , validators=[Length(4,32),optional()])
    password2   = PasswordField(u'パスワード確認' , validators=[
                                                        EqualTo('password', message=u'パスワードと確認用パスワードは一致しません。',)])


class AuthorizeForm(LoginForm):
    pass
