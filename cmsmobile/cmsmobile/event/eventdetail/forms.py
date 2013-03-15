# -*- coding: utf-8 -*-
from wtforms import Form
from wtforms import HiddenField
from wtforms.validators import Optional

class EventDetailForm(Form):

    # --- リンクから受け取る
    event_id = HiddenField(label='', validators=[Optional()], default="0")
    promotion_id = HiddenField(label='', validators=[Optional()], default="0")
    attention_id = HiddenField(label='', validators=[Optional()], default="0")
    topic_id = HiddenField(label='', validators=[Optional()], default="0")

    # --- 表示項目
    event = HiddenField(label='', validators=[Optional()])
    month_unit = HiddenField(label='', validators=[Optional()]) # 月単位の公演
    month_unit_keys = HiddenField(label='', validators=[Optional()]) # month_unitのキー（ソート済み）
    purchase_links = HiddenField(label='', validators=[Optional()]) # performanceのidがキー
    week = HiddenField(label='', validators=[Optional()])
    tickets = HiddenField(label='', validators=[Optional()])
    sales_start = HiddenField(label='', validators=[Optional()])
    sales_end = HiddenField(label='', validators=[Optional()])
