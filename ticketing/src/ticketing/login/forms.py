# -*- coding: utf-8 -*-

from wtforms import TextField, PasswordField, HiddenField
from wtforms.validators import Regexp, Email, Length, EqualTo, Optional, ValidationError
from wtforms import Form

from altair.formhelpers import Translations, Required
from ticketing.operators.models import Operator, OperatorAuth

class LoginForm(Form):

    def _get_translations(self):
        return Translations()

    login_id = TextField(u'ユーザー名', validators=[Required()])
    password = PasswordField(u'パスワード', validators=[Required(), Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。')])

class ResetForm(Form):

    def _get_translations(self):
        return Translations()

    email = TextField(u'メールアドレス', validators=[Required()])

    def validate_email(form, field):
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
    password  = PasswordField(u'パスワード', validators=[Optional(), Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。'), Length(4, 32, message=u'4文字以上32文字以内で入力してください')])
    password2 = PasswordField(u'パスワード確認', validators=[Optional(), EqualTo('password', message=u'パスワードと確認用パスワードが一致しません')])
    expire_at = HiddenField(u'パスワード有効期限', validators=[Optional()])
    
    def validate_login_id(form, field):
        operator_auth = OperatorAuth.get_by_login_id(field.data)
        if operator_auth is not None:
            if operator_auth.operator_id != form.request.context.user.id:
                raise ValidationError(u'ログインIDが重複しています。')
