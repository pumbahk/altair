# -*- coding: utf-8 -*-

from wtforms.form import Form
from wtforms import fields
from wtforms import validators
from ticketing.formhelpers import Translations
from ticketing.operators.models import Operator
from ticketing.core.models import Order

class LoginForm(Form):
    def _get_translations(self):
        return Translations()

    login_id = fields.TextField(u'ユーザー名', validators=[validators.Required()])
    password = fields.PasswordField(u'パスワード', validators=[validators.Required()])

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        self.operator = Operator.login(self.data['login_id'], self.data['password'])
        if self.operator is None:
            self.login_id.errors.append(u'ユーザー名またはパスワードが違います。')
            return False
        return True
            
class MiscOrderFindForm(Form):
    order_no = fields.TextField(u"注文番号", validators=[validators.Required()])

    def object_validate(self, organization_id):
        order_no = self.data["order_no"]
        order = Order.query.filter_by(organization_id=organization_id, order_no=order_no).first()
        if order is None:
            self.order_no.errors.append(u'注文が見つかりません。')
            return False

        self.order = order
        return True

        
