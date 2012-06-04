# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, optional
from wtforms import Form

class AuthorizeForm(Form):
    '''
      Login form
    '''
    login_id    = TextField(u'ユーザー名'         , validators=[Required(message=u'必須項目です。')])
    password    = PasswordField(u'パスワード'    , validators=[Required(message=u'必須項目です。'),Length(4,32,message=u'4文字以上32文字以内で入力してください。')])

