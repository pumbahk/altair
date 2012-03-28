# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.ext.sqlalchemy.fields as extfields
import wtforms.validators as validators

def _pages_accessable():
    ## fixme:
    from altaircms.page.models import Page
    return Page.query.all()

class ReuseChoiceForm(form.Form):
    source_page_id = extfields.QuerySelectField(id="source_page_input", label=u"埋め込みたいページ", 
                                             query_factory=_pages_accessable, allow_blank=False)
    width = fields.IntegerField(id="width_input", label=u"width")
    height = fields.IntegerField(id="height_input", label=u"height")
    ## attrs?
     
