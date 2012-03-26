# -*- coding: utf-8 -*-

from deform.widget import SelectWidget, PasswordWidget, CheckedPasswordWidget, SequenceWidget
from colander import deferred, MappingSchema, SequenceSchema, SchemaNode, String, Int, DateTime, Bool,Length, Decimal, Float, null, Email
import colander

@colander.deferred
def deferred_role_choices_widget(node, kw):
    choices = kw.get('role_choices')
    return SelectWidget(values=choices,min_len=1,max_len=10)

@colander.deferred
def deferred_client_choices_widget(node, kw):
    choices = kw.get('client_choices')
    return SelectWidget(values=choices,min_len=1,max_len=10)

class OperatorRole(SequenceSchema):
    role_id = SchemaNode(Int(), widget=deferred_role_choices_widget, title=u'ロール')

class OperatorForm(MappingSchema):
    client_id   = SchemaNode(Int(), widget=deferred_client_choices_widget)
    email       = SchemaNode(String()   , title=u'Email', validator=Email() )
    name        = SchemaNode(String()   , title=u'名前')
    login_id    = SchemaNode(String()   , title=u'ログインID')
    secret_key  = SchemaNode(String()   , title=u'パスワード', missing=null, widget=CheckedPasswordWidget())
    expire_at   = SchemaNode(DateTime() , title=u'有効期限')
    roles       = OperatorRole(title=u'ロール', validator = Length(1, 10))

class OperatorRoleForm(MappingSchema):
    name = SchemaNode(String())

