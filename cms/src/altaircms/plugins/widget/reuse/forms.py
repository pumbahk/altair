# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
from altaircms.lib.formhelpers import dynamic_query_select_field_factory
import wtforms.validators as validators
from altaircms.page.models import Page

def _pages_accessable():
    ## fixme:
    return Page.query.all()

class ReuseChoiceForm(form.Form):
    source_page_id = dynamic_query_select_field_factory(
        Page,
        id="source_page_input",
        label=u"埋め込みたいページ",
        query_factory=_pages_accessable, allow_blank=False)
    width = fields.IntegerField(id="width_input", label=u"width")
    height = fields.IntegerField(id="height_input", label=u"height")
    ## attrs?
     
