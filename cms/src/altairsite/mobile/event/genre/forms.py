# -*- coding: utf-8 -*-

from wtforms import HiddenField
from wtforms.validators import Optional
from altairsite.mobile.event.search.forms import SearchForm
from altairsite.mobile.forms import TopForm

class GenreForm(SearchForm, TopForm):

    # --- 表示用
    dispgenre = HiddenField(validators=[Optional()])
    dispsubgenre = HiddenField(validators=[Optional()])
    genretree = HiddenField(validators=[Optional()])
