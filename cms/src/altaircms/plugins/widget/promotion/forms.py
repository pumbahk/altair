# -*- coding:utf-8 -*-
import wtforms.form as form
import wtforms.fields as fields
import wtforms.validators as validators
import wtforms.ext.sqlalchemy.fields as extfields
from . import models

def promotion_exists():
    return models.Promotion.query

class PromotionWidgetForm(form.Form):
    promotion = extfields.QuerySelectField(id="promotion", label=u"プロモーション枠", 
                                           get_label=lambda obj: obj.name, 
                                           query_factory = promotion_exists)
    

