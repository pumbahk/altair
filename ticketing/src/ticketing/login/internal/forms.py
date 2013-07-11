# -*- coding: utf-8 -*-class LoginForm(Form):
from wtforms.form import Form
from wtforms import fields
from wtforms import validators
from altair.formhelpers import Translations
from ticketing.operators.models import Operator

class LoginForm(Form):
    def _get_translations(self):
        return Translations()

    login_id = fields.TextField(u'ユーザー名', validators=[validators.Required()])
    password = fields.PasswordField(u'パスワード', validators=[validators.Required(), validators.Regexp("^[a-zA-Z0-9@!#$%&'()*+,\-./_]+$", 0, message=u'英数記号を入力してください。')])

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        self.operator = Operator.login(self.data['login_id'], self.data['password'])
        if self.operator is None:
            self.login_id.errors.append(u'ユーザー名またはパスワードが違います。')
            return False
        return True
