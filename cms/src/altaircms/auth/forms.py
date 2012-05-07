# coding: utf-8
from wtforms.form import Form
from wtforms import fields, widgets, validators
from wtforms.ext.sqlalchemy import fields as sa_fields

from altaircms.models import DBSession
from .models import PERMISSIONS

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
        choices=[(p, p) for p in PERMISSIONS],
    )
