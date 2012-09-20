# coding: utf-8
from wtforms.form import Form
from wtforms import fields, widgets, validators
from wtforms.ext.sqlalchemy import fields as sa_fields

from altaircms.models import DBSession
from .models import PERMISSIONS, OperatorSelfAuth

class SelfLoginForm(Form):
    organization_id = fields.SelectField(
        label=u"所属", 
        choices = [], 
        coerce=unicode, 
        validators=[validators.Required()]
    )
    name = fields.TextField(
        label=u"ユーザ名", 
        validators=[validators.Required()]
    )
    password = fields.TextField(
        label=u"パスワード", 
        validators=[validators.Required()]
    )

    def configure(self, orgs):
        self.organization_id.choices = [(o.id, o.name) for o in orgs]
        return self

    def validate(self):
        super(SelfLoginForm, self).validate()
        if "organization_id" in self.errors:
            del self.errors["organization_id"] # xxx:

        if bool(self.errors):
            return False
        
        self.user = OperatorSelfAuth.get_login_user(
            self.data["organization_id"], 
            self.data["name"], 
            self.data["password"]
            )
        if self.user is None:
            self.errors["name"] = [u"ユーザかパスワードが間違っています"]
            return False
        return True

class APIKeyForm(Form):
    name = fields.TextField(
        validators=[validators.Required()]
    )

class RoleForm(Form):
    permission = fields.SelectField(
        choices=[(p, p) for p in PERMISSIONS],
    )
