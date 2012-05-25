# -*- coding: utf-8 -*-

from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class OrderForm(Form):

    id = HiddenField(
        label=u'ID',
        validators=[Optional()],
    )
    total_amount = HiddenField(
        label=u'合計',
        validators=[Optional()],
    )
    created_at = HiddenField(
        label=u'受注日時',
        validators=[Optional()],
    )
