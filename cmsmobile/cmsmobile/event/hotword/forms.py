# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class HotwordForm(Form):
    id = HiddenField(
        label='',
        validators=[Optional()],
        default="",
    )
