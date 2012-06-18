# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
from altaircms.models import Category
from . import models

class LinklistForm(form.Form):
    _choices = models.FINDER_KINDS_DICT.items()
    finder_kind = fields.SelectField(id="finder_kind", label=u"集めるリンクの種類", choices=_choices)
    delimiter = fields.TextField(id="delimiter", label=u"区切り文字")
    max_items = fields.IntegerField(id="max_items", label=u"最大表示件数", default=20)
    limit_span = fields.IntegerField(id="limit_span", label=u"何日まで範囲に含めるか", default=7)

    _choices = [("-----", u"-----"), ("music", u"音楽"), ("stage", u"演劇"), ("sprots", u"スポーツ"), ("event", u"イベント・その他")]
    genre = fields.SelectField(id="genre", label=u"ジャンル", choices=_choices)
    
