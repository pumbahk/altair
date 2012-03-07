# coding: utf-8
from wtforms.form import Form
from wtforms import fields, widgets, validators

from altaircms.auth.models import Permission
from altaircms.models import DBSession

class OperatorCrudForm(Form):
    pass

class ClientCrudForm(Form):
    pass

class APIKeyForm(Form):
    name = fields.TextField(
        validators=[validators.Required()]
    )

class RoleForm(Form):
    permission = fields.SelectField(
        choices=DBSession.query(Permission.id, Permission.name),
        validators=[validators.Required()],
        coerce=int
    )
