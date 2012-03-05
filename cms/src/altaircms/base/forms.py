# coding: utf-8
from wtforms import form, fields, validators, widgets

class APIKeyForm(form.Form):
    name = fields.TextField(
        validators=[validators.Required()],
        widget=widgets.TextInput({'placeholder':'New APIKEY'})
    )

