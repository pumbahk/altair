# -*- coding: utf-8 -*-

import re

from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import Regexp, Length, EqualTo, Optional, ValidationError
from wtforms import Form

from altair.formhelpers import Translations, Required, ASCII, halfwidth, Email
from altair.app.ticketing.operators.models import Operator, OperatorAuth

class LoginForm(Form):

    def _get_translations(self):
        return Translations()

    login_id = TextField(
        u'ユーザー名',
        filters=[
            halfwidth
            ],
        validators=[
            Required(),
            ASCII
            ]
        )
    password = PasswordField(u'パスワード', validators=[Required(), Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。')])


class SSLClientCertLoginForm(Form):
    def _get_translations(self):
        return Translations()

    password = PasswordField(u'パスワード', validators=[Required(), Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。')])

class ResetForm(Form):

    def _get_translations(self):
        return Translations()

    email = TextField(u'メールアドレス', validators=[Required()])

    def validate_email(self, field):
        if not Operator.filter_by(email=field.data).count():
            raise ValidationError(u'入力されたメールアドレスは登録されていません')

class OperatorForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        Form.__init__(self, formdata, obj, prefix, **kwargs)
        if 'request' in kwargs:
            self.request = kwargs['request']
            
    def _get_translations(self):
        return Translations()

    login_id  = TextField(u'ログインID', validators=[Required()])
    name      = TextField(u'名前', validators=[Required()])
    email     = TextField(u'メールアドレス', validators=[Required(), Email()])
    password  = PasswordField(
        u'パスワード',
        validators=[
            Optional(),
            Regexp(r'^(?=.*[a-zA-Z])(?=.*[0-9])([A-Za-z0-9' + re.escape('~!@#$%^&*()_+-=[]{}|;:<>?,./') + ']+)$', 0,
                   message=u'半角の英文字と数字を組み合わせてご入力ください。大文字も使用できます。'),
            Length(min=7, max=32, message=u'7文字以上32文字以内で入力してください。')
        ]
    )
    password2 = PasswordField(u'パスワード確認', validators=[Optional(), EqualTo('password', message=u'パスワードと確認用パスワードが一致しません。')])
    expire_at = HiddenField(u'パスワード有効期限', validators=[Optional()])
    
    def validate_login_id(self, field):
        operator_auth = OperatorAuth.get_by_login_id(field.data)
        if operator_auth and self.request.context.user:
            if operator_auth.operator_id != self.request.context.user.id:
                raise ValidationError(u'ログインIDが重複しています。')
