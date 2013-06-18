# coding: utf-8
from wtforms import form
from altaircms.formhelpers import Form, fields, validators, widgets
from altaircms.formhelpers import Form

class APIKeyForm(Form):
    name = fields.TextField(
        validators=[validators.Required()],
        widget=widgets.TextInput({'placeholder':'New APIKEY'})
    )

