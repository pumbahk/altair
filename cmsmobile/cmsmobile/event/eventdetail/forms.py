# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class EventDetailForm(Form):

    # --- 表示項目
    event_id = HiddenField(label='', validators=[Optional()], default="0")
    event = HiddenField(label='', validators=[Optional()])
    month_unit = HiddenField(label='', validators=[Optional()]) # 月単位の公演
    month_unit_keys = HiddenField(label='', validators=[Optional()]) # month_unitのキー（ソート済み）
    purchase_links = HiddenField(label='', validators=[Optional()]) # performanceのidがキー
    week = HiddenField(label='', validators=[Optional()])
    tickets = HiddenField(label='', validators=[Optional()])
