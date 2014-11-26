# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class InformationForm(Form):

    # --- 表示用
    information_id = HiddenField(validators=[Optional()])
    information = HiddenField(validators=[Optional()])
    informations = HiddenField(validators=[Optional()])
