# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class InquiryForm(Form):

    # --- 表示用
    informations = HiddenField(validators=[Optional()])
