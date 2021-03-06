# -*- coding: utf-8 -*-
from wtforms import HiddenField
from wtforms.validators import Optional
from altairsite.mobile.core.forms import CommonForm

class SearchForm(CommonForm):

    # --- 曜日表示用
    week = HiddenField(validators=[Optional()])

    # --- パンくずリスト表示用
    navi_genre = HiddenField(validators=[Optional()])
    navi_sub_genre = HiddenField(validators=[Optional()])
    navi_area = HiddenField(validators=[Optional()])

    # --- 表示項目
    events = HiddenField(validators=[Optional()])

    # --- 販売期間
    deal_open = HiddenField(validators=[Optional()])
    deal_close = HiddenField(validators=[Optional()])

class MobileTagSearchForm(SearchForm):

    # --- 表示用
    mobile_tag = HiddenField(validators=[Optional()])
