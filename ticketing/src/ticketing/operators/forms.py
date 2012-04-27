# -*- coding: utf-8 -*-

from deform.widget import SelectWidget, PasswordWidget, CheckedPasswordWidget, SequenceWidget
from colander import deferred, MappingSchema, SequenceSchema, SchemaNode, String, Int, DateTime, Bool,Length, Decimal, Float, null, Email
import colander

from wtforms import TextField, PasswordField, HiddenField, DateField
from wtforms.validators import Required, Email, Length, EqualTo, optional
from wtforms import Form

class OperatorRole(Form):
    pass
class OperatorForm(Form):
    organization_id = HiddenField("", validators=[Required()])
    email       = TextField(u"Email", validators=[Email(),Required()])
    name        = TextField(u"名前", validators=[Required()])
    login_id    = TextField(u"ログインID", validators=[Required()])
    secret_key  = TextField(u"パスワード", validators=[Required()])
    expire_at   = DateField(u"有効期限", validators=[Required()])

class OperatorRoleForm(Form):
    pass

