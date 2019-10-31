# -*- coding: utf-8 -*-

import re

from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import Regexp, Length, EqualTo, Optional, ValidationError
from wtforms import Form
from .fields import DisabledTextField

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
    current_password = PasswordField(u'現在のパスワード', validators=[Required()])
    # 【パスワードは8文字以上とし、以下のうち、3種類以上の要件を満たすこと
    # 大文字アルファベット（A - Z）/ 小文字アルファベット（a - z）/ 数字（0 - 9）/ 記号（!, @,#,%,& 等）】
    password  = PasswordField(
        u'新しいパスワード',
        validators=[
            Optional(),
            Regexp(r'^((?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])|'
                   r'(?=.*[' + re.escape('~!@#$%^&*()_+-=[]{}|;:<>?,./') + '])('
                                                                           r'(?=.*[a-z])(?=.*[A-Z])|'
                                                                           r'(?=.*[a-z])(?=.*[0-9])|'
                                                                           r'(?=.*[A-Z])(?=.*[0-9]))'
                   r')([A-Za-z0-9' + re.escape('~!@#$%^&*()_+-=[]{}|;:<>?,./') + ']+)$', 0,
                   message=u'大文字英字、小文字英字、数字、記号のうち3種類以上の組み合わせでご入力ください。'),
            Length(min=8, max=32, message=u'8文字以上32文字以内で入力してください。')
        ]
    )
    password2 = PasswordField(u'新しいパスワード確認', validators=[Optional(), EqualTo('password', message=u'新しいパスワードと新しい確認用パスワードが一致しません。')])
    expire_at = HiddenField(u'パスワード有効期限', validators=[Optional()])
    
    def validate_login_id(self, field):
        operator_auth = OperatorAuth.get_by_login_id(field.data)
        if operator_auth and self.request.context.user:
            if operator_auth.operator_id != self.request.context.user.id:
                raise ValidationError(u'ログインIDが重複しています。')


class OperatorDisabledForm(OperatorForm):
    login_id = DisabledTextField(u'ログインID')
    name = DisabledTextField(u'名前')
    email = DisabledTextField(u'メールアドレス')
