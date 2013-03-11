# -*- coding: utf-8 -*-
from wtforms import HiddenField
from wtforms.validators import Optional
from cmsmobile.event.search.forms import SearchForm

class HotwordForm(SearchForm):

    # --- 取得用
    id = HiddenField(label='', validators=[Optional()], default="")
