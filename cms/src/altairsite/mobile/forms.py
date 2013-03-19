# -*- coding: utf-8 -*-
from wtforms import HiddenField
from wtforms.validators import Optional
from altairsite.mobile.core.forms import CommonForm

class TopForm(CommonForm):

    # --- 表示項目
    topics = HiddenField(validators=[Optional()])
    promotions = HiddenField(validators=[Optional()])
    attentions = HiddenField(validators=[Optional()])
    hotwords = HiddenField(validators=[Optional()])
    genretree = HiddenField(validators=[Optional()])
