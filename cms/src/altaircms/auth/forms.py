# coding: utf-8
from wtforms.form import Form
from wtforms import fields, widgets, validators
from wtforms.ext.sqlalchemy import fields as sa_fields

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
    permission = sa_fields.QuerySelectField(
        query_factory=lambda: Permission.query,
        get_label=lambda p: p.name,
        validators=[validators.Required()],
    )
