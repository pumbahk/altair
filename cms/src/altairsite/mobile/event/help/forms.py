# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class HelpForm(Form):

    # --- 表示用
    helps = HiddenField(validators=[Optional()])
