# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class DetailForm(Form):

    event_id = HiddenField(validators=[Optional()])
