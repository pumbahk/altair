# coding: utf-8
from wtforms.form import Form
from wtforms import fields, widgets, validators

class OperatorCrudForm(Form):
    pass

class ClientCrudForm(Form):
    pass

class APIKeyForm(Form):
    name = fields.TextField(
        validators=[validators.Required()]
    )
