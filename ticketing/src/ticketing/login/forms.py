# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import Email, Length, EqualTo, Optional, ValidationError
from wtforms import Form

from ticketing.formhelpers import Translations, Required
from ticketing.operators.models import Operator

class LoginForm(Form):

    def _get_translations(self):
        return Translations()

    login_id = TextField(u'ユーザー名', validators=[Required()])
    password = PasswordField(u'パスワード', validators=[Required()])

class ResetForm(Form):

    def _get_translations(self):
        return Translations()

    email = TextField(u'メールアドレス', validators=[Required()])

    def validate_email(form, field):
        if not Operator.filter_by(email=field.data).count():
            raise ValidationError(u'入力されたメールアドレスは登録されていません')

class OperatorForm(Form):

    def _get_translations(self):
        return Translations()

    login_id  = TextField(u'ログインID', validators=[Required()])
    name      = TextField(u'名前', validators=[Required()])
    email     = TextField(u'メールアドレス', validators=[Required(), Email()])
    password  = PasswordField(u'パスワード', validators=[Optional(), Length(4, 32, message=u'4文字以上32文字以内で入力してください')])
    password2 = PasswordField(u'パスワード確認', validators=[Optional(), EqualTo('password', message=u'パスワードと確認用パスワードが一致しません')])
    expire_at = HiddenField(u'パスワード有効期限', validators=[Optional()])
