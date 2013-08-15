# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class OrderReviewForm(Form):

    # --- 購入履歴遷移先
    getti_orderreview_url = HiddenField(validators=[Optional()])
    altair_orderreview_url = HiddenField(validators=[Optional()])
    lots_orderreview_url = HiddenField(validators=[Optional()])
