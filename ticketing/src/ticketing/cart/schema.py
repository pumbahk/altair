# -*- coding:utf-8 -*-

from wtforms import fields, validators
from wtforms.form import Form


class CardForm(Form):
    card_number = fields.TextField(validators=[validators.length(16)])
    exp_year = fields.TextField(validators=[validators.length(2)])
    exp_month = fields.TextField(validators=[validators.length(2)])