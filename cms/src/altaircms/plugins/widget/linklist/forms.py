# -*- coding:utf-8 -*-
from altaircms.formhelpers import Form
import wtforms.fields as fields
import wtforms.validators as validators
from altaircms.models import Genre
from altaircms.formhelpers import dynamic_query_select_field_factory
from altaircms.page.models import PageTag
from . import models

def system_tag_dynamic_query(model, request, query):
    return PageTag.query.filter(PageTag.organization_id==None)
    

class LinklistForm(Form):
    _choices = models.FINDER_KINDS_DICT.items()
    finder_kind = fields.SelectField(id="finder_kind", label=u"集めるリンクの種類", choices=_choices)
    delimiter = fields.TextField(id="delimiter", label=u"区切り文字")
    max_items = fields.IntegerField(id="max_items", label=u"最大表示件数", default=20)
    limit_span = fields.IntegerField(id="limit_span", label=u"何日まで範囲に含めるか", default=7)
    system_tag = dynamic_query_select_field_factory(
        PageTag, allow_blank=True, label=u"ジャンル", break_separate=True, 
        dynamic_query=system_tag_dynamic_query, 
        get_label=lambda obj: obj.label)
